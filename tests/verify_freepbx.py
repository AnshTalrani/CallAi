import socket
import time

def verify_freepbx():
    print("=== FreePBX System Verification ===\n")
    
    # 1. Check if Asterisk is running
    print("1. Checking Asterisk status...")
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "exec", "freepbx", "asterisk", "-rx", "core show version"],
            capture_output=True, text=True
        )
        if "Asterisk" in result.stdout:
            print(f"✅ {result.stdout.strip()}")
        else:
            print(f"❌ Asterisk not running: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ Error checking Asterisk: {str(e)}")
        return
    
    # 2. Check AMI status
    print("\n2. Checking AMI status...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect(('localhost', 5038))
        banner = s.recv(1024).decode('utf-8')
        if "Asterisk" in banner:
            print(f"✅ AMI running: {banner.strip()}")
        else:
            print(f"❌ Unexpected AMI banner: {banner}")
            return
        s.close()
    except Exception as e:
        print(f"❌ AMI connection failed: {str(e)}")
        return
    
    # 3. Check SIP peers
    print("\n3. Checking SIP peers...")
    try:
        result = subprocess.run(
            ["docker", "exec", "freepbx", "asterisk", "-rx", "sip show peers"],
            capture_output=True, text=True
        )
        print(result.stdout.strip())
    except Exception as e:
        print(f"❌ Error checking SIP peers: {str(e)}")
    
    # 4. Check dialplan
    print("\n4. Checking dialplan...")
    try:
        result = subprocess.run(
            ["docker", "exec", "freepbx", "asterisk", "-rx", "dialplan show"],
            capture_output=True, text=True
        )
        print("Loaded contexts:")
        print("\n".join([line for line in result.stdout.split('\n') if 'from-internal' in line]))
    except Exception as e:
        print(f"❌ Error checking dialplan: {str(e)}")
    
    # 5. Test AMI authentication
    print("\n5. Testing AMI authentication...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect(('localhost', 5038))
        s.recv(1024)  # Read banner
        
        # Try to authenticate
        login = "Action: Login\r\nUsername: admin\r\nSecret: admin123\r\n\r\n"
        s.send(login.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        
        if "Authentication accepted" in response or "Response: Success" in response:
            print("✅ AMI authentication successful")
            
            # Test originate command
            print("\n6. Testing call origination...")
            action = (
                "Action: Originate\r\n"
                "Channel: Local/1000@from-internal\r\n"
                "Application: Echo\r\n"
                "\r\n"
            )
            s.send(action.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            print(f"Originate response: {response.strip()}")
            
            if "Success" in response:
                print("✅ Call origination test successful")
            else:
                print("❌ Call origination failed")
                print("Check Asterisk logs for more details")
        else:
            print(f"❌ AMI authentication failed: {response}")
            
        s.close()
    except Exception as e:
        print(f"❌ Error during AMI test: {str(e)}")

if __name__ == "__main__":
    verify_freepbx()
