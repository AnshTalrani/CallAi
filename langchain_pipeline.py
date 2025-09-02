"""LangChain-based modular pipeline conforming to blueprint in `tests/langchain_processing`.

The module defines light-weight class stubs so the rest of the codebase can
incrementally migrate to this unified architecture.  Each component exposes a
`.run()` method that returns its output payload so they can be wired easily
within LangChain `SequentialChain` / `AgentExecutor` objects.

NOTE:  All implementations are placeholders – they only log calls.  Real logic
will be ported from existing services (STT, TTS, CRM, etc.) in upcoming
commits.
"""
from __future__ import annotations

from typing import Dict, Any, List
import logging, json, os

# ---------------------------------------------------------------------------
# A. Input & NLP Layer
# ---------------------------------------------------------------------------
class STTChain:
    """Speech-to-Text using OpenAI Whisper (via HuggingFace transformers).

    Parameters
    ----------
    model_size : str, default "small"
        Whisper checkpoint size to load (tiny, base, small, medium, large).
    device : str, default auto GPU if available else CPU
    """
    def __init__(self, model_size: str | None = None, device: str | None = None):
        import torch
        from transformers import WhisperProcessor, WhisperForConditionalGeneration

        self.sample_rate = 16000
        model_size = model_size or os.environ.get("WHISPER_MODEL_SIZE", "small")
        model_name = f"openai/whisper-{model_size}"
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        logging.info("STTChain initialised with %s on %s", model_name, self.device)

    def run(self, audio_np) -> str:
        """Transcribe 1-D float32 numpy array at 16 kHz mono to text."""
        import torch, numpy as np
        if audio_np is None or not isinstance(audio_np, (list, np.ndarray)):
            return ""
        if isinstance(audio_np, list):
            audio_np = np.array(audio_np, dtype=np.float32)
        # Ensure correct dtype/range
        audio_np = audio_np.astype(np.float32)

        input_features = self.processor(
            audio_np,
            sampling_rate=self.sample_rate,
            return_tensors="pt",
        ).input_features.to(self.device)

        predicted_ids = self.model.generate(
            input_features,
            language="en",
            task="transcribe",
        )
        text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
        logging.debug("STTChain transcription: %s", text)
        return text


class NLPChain:
    """Production NLP layer doing intent + stage classification **and** entity extraction.

    Fast keyword grammar → fallback LLM → CampaignManager entity extraction.
    """

    def __init__(self):
        from services.llm_thinking import LLMThinker  # heavy import kept lazy
        self.thinker = LLMThinker()
        self.cm = CampaignManager()
        # fast keyword patterns
        self.intent_rules = {
            "sales": ["buy", "price", "purchase"],
            "support": ["issue", "problem", "help"],
            "survey": ["survey", "questionnaire"],
        }

    def _keyword_intent(self, transcript_l: str) -> str | None:
        for name, kws in self.intent_rules.items():
            if any(k in transcript_l for k in kws):
                return name
        return None

    def run(self, transcript: str, campaign_id: str | None = None) -> Dict[str, Any]:
        transcript_l = transcript.lower()
        intent = self._keyword_intent(transcript_l) or "unknown"
        stage = "introduction" if intent == "unknown" else "main"
        personality = "default"

        # Fallback to LLM only if still unknown (cheap guard)
        if intent == "unknown":
            prompt = (
                "You are a classifier. Given the user transcript, return JSON with keys intent, stage, personality. "
                "Valid intents: sales, support, survey, other. Valid stages: introduction, main, closing.\n"  # noqa: E501
                f"Transcript: {transcript}\nJSON:"
            )
            try:
                resp = self.thinker.get_response(prompt)
                data = json.loads(resp.strip().split("\n")[-1])
                intent = data.get("intent", intent)
                stage = data.get("stage", stage)
                personality = data.get("personality", personality)
            except Exception as e:
                logging.warning("LLM classification failed: %s", e)

        # Entity extraction via CampaignManager rules when campaign known
        entities: Dict[str, Any] = {}
        if campaign_id:
            try:
                entities = self.cm.extract_data_from_input(campaign_id, transcript) or {}
            except Exception as e:
                logging.debug("Entity extraction failed: %s", e)

        return {
            "intent": intent,
            "stage": stage,
            "entities": entities,
            "personality": personality,
        }


# ---------------------------------------------------------------------------
# B. Campaign Loader
# ---------------------------------------------------------------------------
from core.campaign_manager import CampaignManager  # noqa: E402 (after import guard)

from crm.models.crm import CampaignStage

class CampaignLoader:
    """Fetches full campaign context (template, docs, stage instructions).

    Accepts a *string* stage name coming from the NLP layer and converts it to
    `CampaignStage` enum when possible so downstream code receives a rich
    object and not bare strings.
    """

    def __init__(self):
        # In this context we don't have the authenticated user, so default.
        self.manager = CampaignManager()

    def _to_stage_enum(self, stage: str | None) -> CampaignStage | None:
        if not stage:
            return None
        try:
            return CampaignStage(stage.upper())  # Enum is uppercase names
        except Exception:
            # Fall back to looking up by value attribute
            try:
                return CampaignStage[stage.upper()]
            except Exception:
                return None

    def run(self, campaign_id: str, stage: str | None = None) -> Dict[str, Any]:
        try:
            stage_enum = self._to_stage_enum(stage)
            ctx = self.manager.get_campaign_context(campaign_id, stage_enum, None)
            return ctx or {}
        except Exception as e:
            logging.error("CampaignLoader error: %s", e)
            return {}


# ---------------------------------------------------------------------------
# C. Orchestrator Brain (LLM2)
# ---------------------------------------------------------------------------
class OrchestratorAgent:
    """Production orchestrator leveraging `CampaignManager` for stage logic and tool hints.

    Still keeps optional LLM enrichment but first uses campaign rules.
    """

    def __init__(self, langchain_agent=None):
        from services.llm_thinking import LLMThinker
        self.thinker = LLMThinker()
        self.agent = langchain_agent
        self.cm = CampaignManager()

    def _should_end_call(self, stage: str, transcript: str) -> bool:
        end_phrases = ["bye", "goodbye", "end call", "hang up", "thanks, that's all"]
        return any(p in transcript.lower() for p in end_phrases) or stage == "closing"

    def _rule_next_stage(self, campaign_id: str | None, stage: str, transcript: str) -> str | None:
        if not campaign_id:
            return None
        from crm.models.crm import CampaignStage as CS
        try:
            stage_enum = getattr(CS, stage.upper(), None)
            if not stage_enum:
                return None
            if self.cm.should_transition_stage("conv_dummy", transcript):
                next_enum = self.cm.get_next_stage(campaign_id, stage_enum)
                return next_enum.value if next_enum else None
        except Exception as e:
            logging.debug("CampaignManager transition failed: %s", e)
        return None

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return orchestration dict with CampaignManager-informed decisions."""
        intent = inputs.get("intent", "unknown")
        stage = inputs.get("stage", "introduction")
        transcript = inputs.get("transcript", "")
        campaign_ctx = inputs.get("campaign_ctx", {})
        campaign = campaign_ctx.get("campaign") if isinstance(campaign_ctx, dict) else None
        campaign_id = campaign.id if campaign else None

        # Decision buckets
        restrictions: List[str] = []
        tool_calls: List[Dict[str, Any]] = []

        # 1. Stage transition via CampaignManager or fallback rule
        next_stage = self._rule_next_stage(campaign_id, stage, transcript)

        # 2. Restrictions based on intent or campaign template
        if intent == "sales":
            restrictions.append("Avoid mentioning discounts unless asked")
        if intent == "support":
            restrictions.append("Keep answers within support policy scope")
        if campaign_ctx.get("template") and hasattr(campaign_ctx["template"], "global_restrictions"):
            restrictions.extend(campaign_ctx["template"].global_restrictions)

        # 3. Tool calls declared by stage instructions (template-driven)
        si = campaign_ctx.get("stage_instructions")
        if si and isinstance(si, dict):
            tool_calls.extend(si.get("tool_calls", []))

        call_finished = self._should_end_call(stage, transcript)

        fallback_data = {
            "restrictions": restrictions,
            "next_stage": next_stage,
            "tool_calls": tool_calls,
            "context": {"intent": intent, "stage": stage},
            "call_finished": call_finished,
        }

        # Optional enrichment via LLM2 (do not fail hard)
        try:
            orchestration_prompt = (
                "You are the call orchestrator. Given call data, reply ONLY with JSON having keys "
                "restrictions (list[str]), next_stage (str|null), tool_calls (list[dict]), context (dict).\n"
                f"Data: {json.dumps({**inputs, **fallback_data})}\nJSON:"
            )
            resp = self.thinker.get_response(orchestration_prompt)
            data = json.loads(resp.strip().split("\n")[-1])
            # Merge; LLM output takes precedence when key present
            return {**fallback_data, **data}
        except Exception as e:
            logging.debug("LLM2 orchestration skipped: %s", e)
            return fallback_data


# ---------------------------------------------------------------------------
# D. Responder Brain (LLM1)
# ---------------------------------------------------------------------------
from services.llm_thinking import LLMThinker  # noqa: E402

class ResponderAgent:
    """LLM1 response generator with campaign script preference before LLM free-text."""

    def __init__(self):
        self.thinker = LLMThinker()
        self.cm = CampaignManager()

    def _script_response(self, campaign, stage: str, context: Dict[str, Any], user_input: str) -> str | None:
        try:
            from crm.models.crm import CampaignStage as CS
            stage_enum = getattr(CS, stage.upper(), None)
            if stage_enum:
                return self.cm.get_campaign_script(campaign.id, stage_enum, context, user_input)
        except Exception as e:
            logging.debug("Campaign script retrieval failed: %s", e)
        return None

    def run(self, inputs: Dict[str, Any]) -> str:
        user_input = inputs.get("user_input", "")
        campaign_ctx = inputs.get("campaign", {})
        conv_ctx = inputs.get("context", {})
        restrictions = inputs.get("restrictions", [])

        # 1. Try scripted response
        campaign = campaign_ctx.get("campaign") if isinstance(campaign_ctx, dict) else None
        stage = conv_ctx.get("stage") if isinstance(conv_ctx, dict) else None
        if campaign and stage:
            scripted = self._script_response(campaign, stage, conv_ctx, user_input)
            if scripted:
                return scripted

        # 2. Fallback to LLM
        if restrictions:
            conv_ctx = {**conv_ctx, "restrictions": restrictions}

        return self.thinker.get_response_with_context(
            user_input=user_input,
            campaign_context=campaign_ctx,
            conversation_context=conv_ctx,
        )


# ---------------------------------------------------------------------------
# E. Tool & CRM Agents
# ---------------------------------------------------------------------------
class ToolAgent:
    """Routes tool calls to specialised sub-agents.

    Supported types:
    - crm
    - search  (duckduckgo via LLMThinker)
    - external_api (generic REST call)
    """
    def __init__(self):
        self.crm = CRMAgent()
        from services.llm_thinking import DuckDuckGoSearchAPIWrapper
        self.searcher = DuckDuckGoSearchAPIWrapper()
        import requests
        self._requests = requests

    def run(self, tool_call: Dict[str, Any]) -> Any:
        ttype = tool_call.get("type")
        action = tool_call.get("action")
        payload = tool_call.get("payload", {})
        if ttype == "crm":
            return self.crm.run(action, payload)
        if ttype == "search":
            query = payload.get("query", action)
            return self.searcher.run(query)
        if ttype == "external_api":
            url = payload.get("url")
            method = payload.get("method", "get").lower()
            data = payload.get("data", {})
            try:
                resp = getattr(self._requests, method)(url, json=data, timeout=10)
                return {"status": resp.status_code, "body": resp.text[:2000]}
            except Exception as e:
                return {"error": str(e)}
        logging.warning("Unknown tool type: %s", ttype)
        return {}


from crm.repositories.contact_repository import ContactRepository  # noqa: E402

class CRMAgent:
    """Light wrapper around CRM repository calls with safe error handling."""
    def __init__(self):
        from crm.repositories.campaign_repository import CampaignRepository
        from crm.repositories.conversation_repository import ConversationRepository
        self.contact_repo = ContactRepository()
        self.conv_repo = ConversationRepository()
        self.campaign_repo = CampaignRepository()

    def run(self, action: str, payload: Dict[str, Any]) -> Any:
        logging.debug("CRMAgent.run %s", action)
        try:
            if action == "update_contact_status":
                contact_id = payload.get("contact_id")
                status = payload.get("status")
                if contact_id and status:
                    return self.contact_repo.update_status(contact_id, status)
            elif action == "create_note":
                contact_id = payload.get("contact_id")
                note = payload.get("note")
                if contact_id and note:
                    return self.contact_repo.add_note(contact_id, note)
            elif action == "fetch_next_lead":
                campaign_id = payload.get("campaign_id")
                return self.contact_repo.get_next_lead(campaign_id)
            elif action == "log_call_result":
                conversation_id = payload.get("conversation_id")
                result = payload.get("result")
                if conversation_id and result:
                    return self.conv_repo.add_call_result(conversation_id, result)
        except Exception as e:
            logging.error("CRMAgent error: %s", e)
        logging.warning("Unsupported or failed CRM action %s", action)
        return {}


# ---------------------------------------------------------------------------
# F. Output chains & logger
# ---------------------------------------------------------------------------
from services.text_to_speech import TTSGenerator  # noqa: E402

class TTSChain:
    def __init__(self, voice: str = "af_heart"):
        self.gen = TTSGenerator(default_voice=voice)

    def run(self, text: str) -> bytes:
        logging.debug("TTSChain.run called")
        audio_bytes = self.gen.generate_speech(text, play=False)
        return audio_bytes


class CallLogger:
    """Persist call data for analytics & debugging."""
    def __init__(self):
        from crm.repositories.conversation_repository import ConversationRepository
        self.conv_repo = ConversationRepository()
        self._log_dir = os.environ.get("CALLAI_LOG_DIR", "./call_logs")
        os.makedirs(self._log_dir, exist_ok=True)

    def _write_json(self, data: Dict[str, Any]):
        import uuid, datetime, json as _json
        fname = f"{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}.json"
        path = os.path.join(self._log_dir, fname)
        with open(path, "w", encoding="utf-8") as fp:
            _json.dump(data, fp, ensure_ascii=False, indent=2, default=str)
        return path

    def log(self, data: Dict[str, Any]):
        """Store to repository & file. `data` should include conversation_id if available."""
        logging.debug("CallLogger.log called – keys: %s", list(data.keys()))
        try:
            conv_id = data.get("conversation_id")
            if conv_id:
                self.conv_repo.append_turn(conv_id, data)
        except Exception as e:
            logging.debug("Conversation repo append failed: %s", e)
        # Always write JSON artifact
        self._write_json(data)


# ---------------------------------------------------------------------------
# Composite pipeline for easy integration with CallAgent
# ---------------------------------------------------------------------------
class CallLangChainPipeline:
    """High-level orchestrator tying all components together."""

    def __init__(self):
        self.stt = STTChain()
        self.nlp = NLPChain()
        self.campaign_loader = CampaignLoader()
        self.orchestrator = OrchestratorAgent()
        self.tool_agent = ToolAgent()
        self.responder = ResponderAgent()
        self.tts = TTSChain()
        self.logger = CallLogger()

    # -------------------- internal helpers --------------------
    def _safe(self, func, *args, default=None, **kwargs):
        """Execute func returning `default` on any Exception; log stack trace."""
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.exception("%s failed – returning fallback", getattr(func, "__name__", str(func)))
            return default

    # This method should eventually be converted to a LangChain Graph/SequentialChain.
    def run_step(self, audio_input, campaign_id: str, crm_context: Dict[str, Any]) -> Dict[str, Any]:
        transcript = self._safe(self.stt.run, audio_input, default="")
        nlp_out = self._safe(self.nlp.run, transcript, campaign_id, default={"intent": "unknown", "stage": "introduction", "entities": {}})
        campaign_ctx = self._safe(self.campaign_loader.run, campaign_id, nlp_out.get("stage"), default={})

        orchestrator_defaults = {"restrictions": [], "next_stage": None, "tool_calls": [], "context": {}, "call_finished": False}
        orchestrator_out = self._safe(
            self.orchestrator.run,
            {
                **nlp_out,
                **crm_context,
                "transcript": transcript,
                "campaign_ctx": campaign_ctx,
            },
            default=orchestrator_defaults,
        )

        # Execute tool calls immediately
        for call in orchestrator_out.get("tool_calls", []):
            self.tool_agent.run(call)

        response = self._safe(
            self.responder.run,
            {
                "user_input": transcript,
                "restrictions": orchestrator_out.get("restrictions", []),
                "campaign": campaign_ctx,
                "context": orchestrator_out.get("context", {}),
            },
            default="",
        )

        tts_audio = self._safe(self.tts.run, response, default=b"")

        # Determine if this turn should end the call
        end_keywords = ["bye", "goodbye", "end call", "hang up"]
        call_finished = False
        if any(k in transcript.lower() for k in end_keywords):
            call_finished = True
        # Heuristic: if orchestrator has no next_stage and stage is closing
        if orchestrator_out.get("next_stage") is None and orchestrator_out.get("context", {}).get("stage") == "closing":
            call_finished = True

        self.logger.log({
            "conversation_id": crm_context.get("conversation_id"),
            "transcript": transcript,
            "response": response,
            "stage": nlp_out.get("stage"),
            "tool_calls": orchestrator_out.get("tool_calls", []),
        })
        return {
            "response": response,
            "tts_audio": tts_audio,
            "call_finished": call_finished,
            "next_stage": orchestrator_out.get("next_stage")
        }
