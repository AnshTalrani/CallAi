import os
import logging
from CallAi.telephony.freepbx_integration import FreePBXIntegration

logging.basicConfig(level=logging.INFO)

def main():
    # Load settings from env or use defaults suitable for local dev
    host = os.getenv("FREEPBX_HOST", "127.0.0.1")
    port = int(os.getenv("FREEPBX_AMI_PORT", "5038"))
    user = os.getenv("FREEPBX_AMI_USER", "admin")
    pwd = os.getenv("FREEPBX_AMI_PASS", "amp111")

    pbx = FreePBXIntegration(host, port, user, pwd)
    resp = pbx.originate_call(
        from_number="1000",
        to_number="1001",
        context="from-internal",
    )
    print("Originate response:", resp)

if __name__ == "__main__":
    main()
