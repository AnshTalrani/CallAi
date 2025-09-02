# Attempt to import the real ARI client. If unavailable (e.g. in local dev
# environments without Asterisk), provide a lightweight stub so the rest of
# the application can still run.
try:
    import ari  # type: ignore
except ImportError:  # pragma: no cover – allow offline development
    import logging

    logging.warning("ARI SDK not available – using dummy telephony client. Calls will be no-ops.")

    class _DummyChannel:
        def hold(self):
            logging.info("[DummyARI] hold() called – no effect")

        def unhold(self):
            logging.info("[DummyARI] unhold() called – no effect")

        def redirect(self, **kwargs):
            logging.info("[DummyARI] redirect() called – no effect")

        def send_dtmf(self, *_, **__):
            logging.info("[DummyARI] send_dtmf() called – no effect")

    class _DummyChannels:
        def originate(self, **kwargs):
            logging.info("[DummyARI] originate() called – no effect")
            return _DummyChannel()

        def get(self, **kwargs):
            logging.info("[DummyARI] get() called – returning dummy channel")
            return _DummyChannel()

    class _DummyClient:
        channels = _DummyChannels()

    class _DummyARI:
        @staticmethod
        def connect(*_, **__):  # noqa: D401,E501 – signature matches real API
            return _DummyClient()

    ari = _DummyARI  # type: ignore

import logging
from typing import Optional, Callable

class AsteriskIntegration:
    """
    Handles integration with Asterisk via ARI for outbound/inbound calls and call control.
    """
    def __init__(self, ari_url: str, username: str, password: str):
        self.ari_url = ari_url
        self.username = username
        self.password = password
        self.client = ari.connect(ari_url, username, password)
        logging.info(f"Connected to Asterisk ARI at {ari_url}")

    def originate_call(self, from_number: str, to_number: str, context: str = 'default', extension: str = None, callback: Optional[Callable] = None):
        """
        Originate an outbound call from from_number to to_number.
        """
        if extension is None:
            extension = to_number
        logging.info(f"Originating call from {from_number} to {to_number} (context: {context}, extension: {extension})")
        try:
            channel = self.client.channels.originate(
                endpoint=f"PJSIP/{to_number}",
                callerId=from_number,
                context=context,
                extension=extension,
                priority=1,
                app='Stasis',
                appArgs='callai',
                timeout=30
            )
            if callback:
                callback(channel)
            return channel
        except Exception as e:
            logging.error(f"Failed to originate call: {e}")
            return None

    def hold_call(self, channel_id: str):
        """Put a call on hold (stub)."""
        try:
            channel = self.client.channels.get(channelId=channel_id)
            channel.hold()
            logging.info(f"Call {channel_id} put on hold.")
        except Exception as e:
            logging.error(f"Failed to hold call {channel_id}: {e}")

    def unhold_call(self, channel_id: str):
        """Remove hold from a call (stub)."""
        try:
            channel = self.client.channels.get(channelId=channel_id)
            channel.unhold()
            logging.info(f"Call {channel_id} removed from hold.")
        except Exception as e:
            logging.error(f"Failed to unhold call {channel_id}: {e}")

    def transfer_call(self, channel_id: str, new_extension: str, context: str = 'default'):
        """Transfer a call to a new extension (stub)."""
        try:
            channel = self.client.channels.get(channelId=channel_id)
            channel.redirect(context=context, extension=new_extension, priority=1)
            logging.info(f"Call {channel_id} transferred to {new_extension}.")
        except Exception as e:
            logging.error(f"Failed to transfer call {channel_id}: {e}")

    def send_dtmf(self, channel_id: str, dtmf: str):
        """Send DTMF tones to a call (stub)."""
        try:
            channel = self.client.channels.get(channelId=channel_id)
            channel.send_dtmf(dtmf)
            logging.info(f"Sent DTMF '{dtmf}' to call {channel_id}.")
        except Exception as e:
            logging.error(f"Failed to send DTMF to call {channel_id}: {e}")

    def track_call_outcome(self, call_id: str, outcome: str, notes: str = None):
        """Track the outcome of a call (stub for analytics)."""
        # This would update the call record in the DB with outcome and notes
        logging.info(f"Call {call_id} outcome: {outcome} ({notes})")

    def handle_inbound_call(self, event):
        """Handle inbound call event from ARI (stub)."""
        # This would be hooked into the ARI event loop
        logging.info(f"Inbound call event: {event}")
