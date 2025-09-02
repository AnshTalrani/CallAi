import socket
import time

def test_ami_connection(host='localhost', port=5038, username='admin', secret='admin123'):
    try:
        # Create a socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        # Set a timeout for receiving data
        s.settimeout(5.0)
        
        # Read the banner
        try:
            banner = s.recv(1024).decode('utf-8')
            print("Banner:", banner.strip())
        except socket.timeout:
            return "Error: Timeout waiting for banner. Check if AMI is running on the specified port."
        
        # Send login
        login = f"Action: Login\r\nUsername: {username}\r\nSecret: {secret}\r\n\r\n"
        s.send(login.encode('utf-8'))
        
        # Get response
        response = s.recv(1024).decode('utf-8')
        
        # Check for successful authentication
        if "Response: Success" not in response or "Message: Authentication accepted" not in response:
            return f"Login failed. Response: {response}"
        print("\nLogin Response:")
        print(response.strip())
            
        if "Authentication failed" in response:
            return "Error: Authentication failed. Check username and password."
                
            return "Error: Timeout waiting for login response."
        
        # Send ping to verify connection
        s.send(b"Action: Ping\r\n\r\n")
        ping_response = s.recv(1024).decode('utf-8')
        print("\nPing Response:")
        print(ping_response.strip())
        
        # Logout
        s.send(b"Action: Logoff\r\n\r\n")
        s.close()
        
        return "Successfully connected and authenticated with AMI"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(test_ami_connection())
