# SIP Integration with FreePBX

This document provides information about the SIP telephony integration in the CallAI system using FreePBX.

## Prerequisites

1. FreePBX server with AMI (Asterisk Manager Interface) enabled
2. Python 3.8+
3. Required Python packages (see `requirements.txt`)

## Environment Variables

Set these environment variables in your `.env` file or system environment:

```bash
# FreePBX/AMI Configuration
FREEPBX_HOST=localhost          # FreePBX server address
FREEPBX_AMI_PORT=5038          # AMI port (default: 5038)
FREEPBX_AMI_USER=admin         # AMI username
FREEPBX_AMI_PASS=your_password # AMI password

# SIP Configuration
SIP_DOMAIN=your_domain.com     # SIP domain
SIP_USER=1000                  # Default SIP extension
SIP_PASSWORD=your_password     # SIP password
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure FreePBX**:
   - Enable AMI in FreePBX
   - Create SIP extensions (1000, 1001, etc.)
   - Set up appropriate dialplan

3. **Test Connection**:
   ```bash
   python tests/test_ami_connection.py
   ```

## Usage

### Making a Call

```python
from telephony.freepbx_integration import FreePBXIntegration

# Initialize with environment variables or custom settings
pbx = FreePBXIntegration(
    host=os.getenv('FREEPBX_HOST'),
    port=int(os.getenv('FREEPBX_AMI_PORT', 5038)),
    username=os.getenv('FREEPBX_AMI_USER'),
    password=os.getenv('FREEPBX_AMI_PASS')
)

# Make a call
pbx.originate_call(
    from_number='1000',
    to_number='1001',
    context='from-internal',
    timeout=30000
)
```

### Receiving Calls

Implement call handling in your application using the `CallAgent` class:

```python
from core.call_agent import CallAgent

agent = CallAgent()
# The agent will handle incoming calls based on registered handlers
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify AMI credentials in `/etc/asterisk/manager.conf`
   - Check if the AMI user has correct permissions

2. **No SIP Registration**
   - Verify SIP peers are properly configured
   - Check network connectivity between client and server
   - Verify SIP credentials and domain settings

3. **Call Drops**
   - Check network stability
   - Verify codec compatibility
   - Check NAT/firewall settings

### Checking Logs

View Asterisk logs:
```bash
docker exec freepbx tail -f /var/log/asterisk/full
```

## Security Considerations

1. Always use strong passwords for AMI and SIP accounts
2. Restrict AMI access to trusted IPs
3. Use TLS for SIP traffic in production
4. Regularly update FreePBX and Asterisk

## Resources

- [FreePBX Documentation](https://wiki.freepbx.org/display/FPG/FreePBX+Documentation)
- [Asterisk AMI Documentation](https://wiki.asterisk.org/wiki/display/AST/Asterisk+16+AMI+Actions)
- [SIP Protocol Reference](https://tools.ietf.org/html/rfc3261)
