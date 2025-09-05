from __future__ import annotations

"""FreePBX telephony backend using the Asterisk Manager Interface (AMI).
This mirrors the public surface of `AsteriskIntegration` so that the wider
codebase can switch telephony back-ends by changing a single import.

Only a subset of AMI commands are wrapped – enough for simple outbound call
origination and a few call-control helpers.  All other methods are safe no-ops
that log an informative message, so the application can continue to run even
if the FreePBX server is unreachable during development.
"""

import logging
from typing import Optional, Callable, Any

try:
    # Prefer the widely-used 'python-asterisk' library (package name 'asterisk-ami' provides modules under 'asterisk').
    from asterisk.ami import AMIClient  # type: ignore
    from asterisk.ami import SimpleAction  # type: ignore
except ImportError:  # pragma: no cover – allow offline development without deps

    class _DummyResponse:  # noqa: D401
        success = False
        response = "Error"
        message = "asterisk_ami not installed – dummy response"

        def __repr__(self) -> str:  # noqa: D401
            return f"<_DummyResponse success={self.success} msg={self.message}>"

    class _DummyManager:  # noqa: D401
        def login(self, *_: Any, **__: Any) -> None:  # noqa: D401
            logging.warning(
                "asterisk_ami not available – using dummy telephony client. "
                "Calls will be no-ops."
            )

        def send_action(self, *_: Any, **__: Any) -> _DummyResponse:  # noqa: D401
            logging.info("[DummyAMI] send_action() called – no effect")
            return _DummyResponse()

        def logoff(self) -> None:  # noqa: D401
            pass

    AMIClient = _DummyManager  # type: ignore
    SimpleAction = dict  # type: ignore


class FreePBXIntegration:  # noqa: D101
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5038,
        username: str = "admin",
        password: str = "amp111",
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        # Establish AMI connection
        try:
            self.client: AMIClient = AMIClient(address=host, port=port)  # type: ignore[arg-type]
            self.client.login(username=username, secret=password)
            logging.info("Connected to FreePBX AMI at %s:%s as %s", host, port, username)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to connect to FreePBX AMI: %s", exc)
            self.client = None

    # ------------------------------------------------------------------
    # Dial / originate
    # ------------------------------------------------------------------
    def originate_call(
        self,
        from_number: str,
        to_number: str,
        context: str = "from-internal",
        extension: Optional[str] = None,
        priority: int = 1,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> Any:  # noqa: ANN401 – depends on AMI response type
        """Originate an outbound call.

        FreePBX typically uses the *from-internal* context for devices/softphones
        registered on the PBX.  Adjust `context` if your dial-plan differs.
        """
        if extension is None:
            extension = to_number

        if self.client is None:
            logging.warning("No AMI connection – simulate originate success")
            return True

        action = SimpleAction(
            'Originate',
            Channel=f'SIP/{to_number}',
            Exten=extension,
            Context=context,
            Priority=priority,
            CallerID=from_number,
            Timeout=30000,
        )
        logging.info("[FreePBX] originate: %s", action)
        try:
            resp = self.client.send_action(action)
            if callback:
                callback(resp)
            return resp.response if hasattr(resp, 'response') else resp
        except Exception as exc:  # noqa: BLE001
            logging.error("AMI originate failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Call-control helpers – implemented as safe stubs.
    # ------------------------------------------------------------------
    def hold_call(self, channel: str) -> None:  # noqa: D401
        logging.info("[FreePBX] hold_call %s (stub)", channel)

    def unhold_call(self, channel: str) -> None:  # noqa: D401
        logging.info("[FreePBX] unhold_call %s (stub)", channel)

    def transfer_call(self, channel: str, new_extension: str, context: str = "from-internal") -> None:  # noqa: D401,E501
        logging.info("[FreePBX] transfer_call %s -> %s (context %s) (stub)", channel, new_extension, context)

    def send_dtmf(self, channel: str, dtmf: str) -> None:  # noqa: D401
        logging.info("[FreePBX] send_dtmf %s to %s (stub)", dtmf, channel)

    def track_call_outcome(self, call_id: str, outcome: str, notes: Optional[str] = None) -> None:  # noqa: D401,E501
        logging.info("Call %s outcome: %s (%s)", call_id, outcome, notes)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def __del__(self) -> None:  # noqa: D401
        if hasattr(self, "manager") and getattr(self.manager, "logoff", None):
            try:
                self.manager.logoff()
            except Exception:  # pragma: no cover
                pass
