import socket
print("Testing connection...")
try:
    # Try to ping Google's server (8.8.8.8)
    socket.create_connection(("8.8.8.8", 53), timeout=2)
    print("✅ Internet is WORKING!")
except OSError:
    print("❌ Internet is BROKEN. The Pi cannot reach the outside world.")