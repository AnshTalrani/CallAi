import socket
import time

def debug_ami_connection(host='localhost', port=5038):
    try:
        # Create a socket connection
        print(f"Connecting to {host}:{port}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((host, port))
        
        # Read the banner
        print("\nReading banner...")
        banner = s.recv(1024).decode('utf-8')
        print(f"Banner: {banner!r}")
        
        # Test login with different credentials
        test_creds = [
            ('admin', 'admin123'),
            ('admin', '7db2501bcc9812c51577f68a31a72587'),
            ('admin', 'amp111')
        ]
        
        for username, secret in test_creds:
            print(f"\nTrying login with {username}:{secret}")
            login = f"Action: Login\r\nUsername: {username}\r\nSecret: {secret}\r\n\r\n"
            s.send(login.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            print(f"Response: {response!r}")
            
            if "Authentication accepted" in response or "Response: Success" in response:
                print("Login successful!")
                s.send(b"Action: Logoff\r\n\r\n")
                return "Success"
                
        s.close()
        return "All login attempts failed"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(debug_ami_connection())
