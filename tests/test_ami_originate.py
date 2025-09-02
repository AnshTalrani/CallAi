import socket
import time

def originate_call(
    host='localhost',
    port=5038,
    username='admin',
    secret='admin123',
    from_number='1000',
    to_number='1001',
    context='from-internal',
    extension='1001',
    priority=1
):
    try:
        print(f"Connecting to AMI at {host}:{port}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((host, port))
        
        # Read banner
        banner = s.recv(1024).decode('utf-8')
        print(f"Banner: {banner.strip()!r}")
        
        # Login
        print(f"Authenticating as {username}...")
        login = f"Action: Login\r\nUsername: {username}\r\nSecret: {secret}\r\n\r\n"
        s.send(login.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        
        if "Authentication accepted" not in response and "Response: Success" not in response:
            return f"Login failed. Response: {response}"
            
        print("Successfully authenticated with AMI")
            
        # Build originate action
        action = (
            f"Action: Originate\r\n"
            f"Channel: SIP/{to_number}\r\n"
            f"Exten: {extension}\r\n"
            f"Context: {context}\r\n"
            f"Priority: {priority}\r\n"
            f"Callerid: {from_number}\r\n"
            f"Timeout: 30000\r\n"
            f"Async: true\r\n\r\n"
        )
        
        print(f"Originating call from {from_number} to {to_number}...")
        s.send(action.encode('utf-8'))
        
        # Get response
        response = s.recv(1024).decode('utf-8')
        print("\nOriginate Response:")
        print(response.strip())
        
        # Logout
        s.send(b"Action: Logoff\r\n\r\n")
        s.close()
        
        return "Call originated successfully!"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Testing AMI Originate...")
    print(originate_call())
