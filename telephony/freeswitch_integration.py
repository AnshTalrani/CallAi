"""FreeSWITCH integration via Event Socket Library (ESL).
This mirrors the public surface of `AsteriskIntegration` so the rest of the
codebase can switch telephony back-ends by simple import.
"""
from __future__ import annotations

import logging
import os
from typing import Optional, Callable

# Try official C bindings first, then fallback to pure-python greenswitch.
try:
    import ESL  # type: ignore
    _ESL_MODE = "c"
except ImportError:  # pragma: no cover – offline/dev mode
    try:
        from greenswitch.esl import ESLConnection as _GSConnection  # type: ignore
        _ESL_MODE = "greenswitch"
    except ImportError:
        logging.warning("No ESL bindings available – using dummy telephony client. Calls will be no-ops.")
        _ESL_MODE = "dummy"

    class _DummyESLConnection:  # noqa: D401
        def __init__(self, *_, **__):
            pass

        def api(self, *_, **__):
            return type("Resp", (), {"getBody": lambda self: ""})()  # type: ignore

    class ESL:  # type: ignore
        Connection = _DummyESLConnection


class FreeSwitchIntegration:
    """Wrapper around FreeSWITCH ESL providing call-control helpers."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8021, password: str = "ClueCon"):
        self.host = host
        self.port = port
        self.password = password
        if _ESL_MODE == "c":
            self.conn = ESL.Connection(host, str(port), password)  # type: ignore
        elif _ESL_MODE == "greenswitch":
            self.conn = _GSConnection(host, port, password)  # type: ignore
            try:
                self.conn.connect()
            except Exception as exc:  # noqa: BLE001
                logging.error("Failed to connect via greenswitch: %s", exc)
                self.conn = None
        else:
            self.conn = None

        if self.conn and getattr(self.conn, "connected", lambda: True)():
            logging.info("Connected to FreeSWITCH (%s bindings) at %s:%s", _ESL_MODE, host, port)
        else:
            logging.error("Failed to connect to FreeSWITCH (%s bindings) at %s:%s", _ESL_MODE, host, port)

    # ---------------------------------------------------------------------
    # Dial / originate
    # ---------------------------------------------------------------------
    def originate_call(
        self,
        from_number: str,
        to_number: str,
        context: str = "public",
        extension: Optional[str] = None,
        gateway: Optional[str] = None,
        callback: Optional[Callable] = None,
    ):
        """Originate an outbound call.

        Uses the `originate` API command.
        """
        if extension is None:
            extension = to_number

        if gateway is None:
            gateway = os.getenv("FS_GATEWAY", "sofia/gateway/mygw")

        dial_str = f"{gateway}/{to_number} &park()"
        cmd = f"bgapi originate {{origination_caller_id_number={from_number}}}{dial_str}"
        logging.info("[FreeSWITCH] originate: %s", cmd)
        if not self.conn or not getattr(self.conn, "api", None):
            logging.warning("No ESL connection – simulate originate success for dev mode")
            return True  # Dummy success
        try:
            resp = self.conn.api(cmd)
        except Exception as exc:  # noqa: BLE001
            logging.error("ESL originate failed: %s", exc)
            return None
        if callback:
            callback(resp)
        return resp

    # ------------------------------------------------------------------
    # Call control helpers (no-op stubs if not connected)
    # ------------------------------------------------------------------
    def _run_bgapi(self, command: str):
        logging.info("[FreeSWITCH] %s", command)
        if self.conn and getattr(self.conn, "bgapi", None):
            try:
                self.conn.bgapi(command)
            except Exception as exc:  # noqa: BLE001
                logging.error("ESL command failed: %s", exc)

    def hold_call(self, uuid: str):
        self._run_bgapi(f"uuid_hold {uuid} true")

    def unhold_call(self, uuid: str):
        self._run_bgapi(f"uuid_hold {uuid} false")

    def transfer_call(self, uuid: str, new_extension: str, context: str = "public"):
        self._run_bgapi(f"uuid_transfer {uuid} {new_extension} {context}")

    def send_dtmf(self, uuid: str, dtmf: str):
        self._run_bgapi(f"uuid_send_dtmf {uuid} {dtmf}")

    def track_call_outcome(self, call_id: str, outcome: str, notes: Optional[str] = None):
        logging.info("Call %s outcome: %s (%s)", call_id, outcome, notes)
