import socket
import time
import threading


SERVER_IP = "10.0.0.5"
SERVER_PORT = 5555
BUFFER_SIZE = 4096


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
    print("🔍 Test: Third client should be blocked...")

    result1 = simulate_client("Player1")
    result2 = simulate_client("Player2")
    result3 = simulate_client("Player3")

    assert result1 != "FULL", "Player1 should be allowed"
    assert result2 != "FULL", "Player2 should be allowed"
    assert result3 == "FULL", "Player3 should be rejected"

    print("✅ Passed: Third player was blocked correctly.\n")


def test_server_crash_detection():
    print("🔍 Test: Server crash simulation...")

    print(">>> Please STOP the server manually for 5 seconds NOW...")
    time.sleep(5)

    result = simulate_client("ReconnectAfterCrash")
    assert result in ["NO_RESPONSE", "FULL", "ERROR"], "Client should not crash"
    print("✅ Passed: Client handled server down gracefully.\n")


if __name__ == "__main__":
    test_third_client_blocked()
    test_server_crash_detection()
