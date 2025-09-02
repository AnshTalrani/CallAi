import socket
import time

def test_outbound_call():
    host = 'localhost'
    port = 5038
    username = 'admin'
    secret = 'admin123'
    
    print("=== Testing Outbound Call ===\n")
    
    # 1. Test basic socket connection
    print("1. Testing socket connection...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10.0)
        s.connect((host, port))
        print("✅ Successfully connected to AMI")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # 2. Read banner
    try:
        banner = s.recv(1024).decode('utf-8')
        print(f"✅ Received banner: {banner.strip()!r}")
    except Exception as e:
        print(f"❌ Failed to read banner: {e}")
        s.close()
        return
    
    # 3. Test authentication
    print("\n2. Testing authentication...")
    try:
        login = f"Action: Login\r\nUsername: {username}\r\nSecret: {secret}\r\n\r\n"
        s.send(login.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        
        if "Authentication accepted" in response or "Response: Success" in response:
            print("✅ Authentication successful")
            print(f"   Response: {response.strip()}")
        else:
            print(f"❌ Authentication failed. Response: {response}")
            s.close()
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        s.close()
        return
    
    # 4. Test call origination
    print("\n3. Testing call origination...")
    try:
        action = (
            "Action: Originate\r\n"
            "Channel: SIP/1001\r\n"  # Destination extension
            "Exten: 1001\r\n"
            "Context: from-internal\r\n"
            "Priority: 1\r\n"
            "Callerid: 1000\r\n"    # Source extension
            "Timeout: 30000\r\n"
            "Async: true\r\n"
            "\r\n"
        )
        print("   Sending originate command...")
        s.send(action.encode('utf-8'))
        
        # Wait for response
        response = s.recv(1024).decode('utf-8')
        print(f"   Originate response: {response.strip()!r}")
        
        if "successfully queued" in response or "Success" in response:
            print("✅ Call origination successful")
        else:
            print("❌ Call origination failed")
            
    except Exception as e:
        print(f"❌ Call origination error: {e}")
    finally:
        # Clean up
        try:
            s.send(b"Action: Logoff\r\n\r\n")
            s.close()
        except:
            pass

if __name__ == "__main__":
    test_outbound_call()
