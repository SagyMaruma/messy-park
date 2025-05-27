import socket
import time
import threading
import subprocess
import os

SERVER_IP = "10.0.0.5"
SERVER_PORT = 5555
BUFFER_SIZE = 4096
SERVER_PROCESS = None

def start_server():
    global SERVER_PROCESS
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server", "server.py"))
    SERVER_PROCESS = subprocess.Popen(["python", server_path])
    print("🟢 Server started for test...")
    time.sleep(1.5)  # המתנה לשרת שיתחיל להאזין

def stop_server():
    global SERVER_PROCESS
    if SERVER_PROCESS:
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait()
        print("🛑 Server terminated.")

def simulate_client(name):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(3)
        client_socket.sendto(name.encode(), (SERVER_IP, SERVER_PORT))

        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        decoded = response.decode()

        if decoded == "FULL":
            print(f"[{name}] ❌ Server is full.")
            return "FULL"

        print(f"[{name}] ✅ Joined as: {decoded}")
        return decoded

    except socket.timeout:
        print(f"[{name}] ⚠ No response (maybe server down)")
        return "NO_RESPONSE"
    except Exception as e:
        print(f"[{name}] ❌ Error: {e}")
        return "ERROR"
    finally:
        client_socket.close()

def test_third_client_blocked():
    print("\n🔍 Test: Third client should be blocked...")
    start_server()

    result1 = simulate_client("Player1")
    time.sleep(0.5)
    result2 = simulate_client("Player2")
    time.sleep(0.5)
    result3 = simulate_client("Player3")

    stop_server()

    assert result1 != "FULL", "Player1 should be allowed"
    assert result2 != "FULL", "Player2 should be allowed"
    assert result3 == "FULL", "Player3 should be rejected"

    print("✅ Passed: Third player was blocked correctly.\n")

def test_server_crash_detection():
    print("\n🔍 Test: Server crash simulation (auto)...")
    start_server()

    stop_server()
    time.sleep(1)

    result = simulate_client("ReconnectAfterCrash")
    assert result in ["NO_RESPONSE", "FULL", "ERROR"], "Client should not crash"
    print("✅ Passed: Client handled server down gracefully.\n")

if __name__ == "__main__":
    test_third_client_blocked()
    test_server_crash_detection()