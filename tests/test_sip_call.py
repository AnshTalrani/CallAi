import socket
import time

def test_sip_call():
    host = 'localhost'
    port = 5038
    username = 'admin'
    secret = 'admin123'
    
    print("=== Testing SIP Call Setup ===\n")
    
    try:
        # Connect to AMI
        print("1. Connecting to AMI...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10.0)
        s.connect((host, port))
        
        # Read banner
        banner = s.recv(1024).decode('utf-8')
        if not banner.startswith('Asterisk'):
            print(f"❌ Unexpected banner: {banner}")
            return
        print("✅ Connected to AMI")
        
        # Login
        login = f"Action: Login\r\nUsername: {username}\r\nSecret: {secret}\r\n\r\n"
        s.send(login.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        
        if "Authentication accepted" not in response and "Response: Success" not in response:
            print(f"❌ Login failed. Response: {response}")
            return
        print("✅ Authenticated with AMI")
        
        # Originate call from 1000 to 1001
        print("\n2. Originating call from 1000 to 1001...")
        action = (
            "Action: Originate\r\n"
            "Channel: Local/1000@from-internal\r\n"
            "Exten: 1001\r\n"
            "Context: from-internal\r\n"
            "Priority: 1\r\n"
            "Callerid: 1000\r\n"
            "Timeout: 30000\r\n"
            "Async: true\r\n"
            "\r\n"
        )
        s.send(action.encode('utf-8'))
        
        # Get response
        response = s.recv(1024).decode('utf-8')
        print(f"Originate response: {response.strip()}")
        
        if "successfully queued" in response or "Success" in response:
            print("✅ Call originated successfully")
        else:
            print("❌ Failed to originate call")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        try:
            s.send(b"Action: Logoff\r\n\r\n")
            s.close()
        except:
            pass

if __name__ == "__main__":
    test_sip_call()
