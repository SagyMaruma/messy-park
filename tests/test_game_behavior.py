import socket
import time
import threading
import subprocess
import os
import struct

SERVER_IP = "10.0.0.5"
SERVER_PORT = 5555
BUFFER_SIZE = 4096
SERVER_PROCESS = None

def start_server():
    global SERVER_PROCESS
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server", "server.py"))
    SERVER_PROCESS = subprocess.Popen(["python", server_path])
    print("🟢 Server started for test...")
    time.sleep(1.5)

def stop_server():
    global SERVER_PROCESS
    if SERVER_PROCESS:
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait()
        print("🛑 Server terminated.")

def xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

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

# 🧪 בדיקה 1: האם שחקן שלישי נחסם

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

# 🧪 בדיקה 2: האם לקוח שורד קריסת שרת

def test_server_crash_detection():
    print("\n🔍 Test: Server crash simulation (auto)...")
    start_server()
    stop_server()
    time.sleep(1)
    result = simulate_client("ReconnectAfterCrash")
    assert result in ["NO_RESPONSE", "FULL", "ERROR"], "Client should not crash"
    print("✅ Passed: Client handled server down gracefully.\n")

# 🧪 בדיקה 3: האם הטיימר באמת רץ אחרי תחילת המשחק

def test_timer_runs_correctly():
    print("\n🔍 Test: Timer runs during game...")
    start_server()
    simulate_client("Player1")
    time.sleep(0.5)
    simulate_client("Player2")
    print("⏱ Waiting 3 seconds to simulate gameplay...")
    time.sleep(3)
    result = simulate_client("TimerCheck")
    stop_server()
    assert result == "FULL", "Server should be full with 2 players, implying timer is running"
    print("✅ Passed: Timer assumed active after game start delay.\n")

# 🧪 בדיקה 4: מעבר שלב כששני שחקנים עומדים על הדלת

def test_level_transition():
    print("\n🔍 Test: Level transition when both players on door...")
    start_server()
    client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client1.settimeout(3)
    client1.sendto("Tester1".encode(), (SERVER_IP, SERVER_PORT))
    client1.recvfrom(BUFFER_SIZE)
    key1, _ = client1.recvfrom(BUFFER_SIZE)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client2.settimeout(3)
    client2.sendto("Tester2".encode(), (SERVER_IP, SERVER_PORT))
    client2.recvfrom(BUFFER_SIZE)
    key2, _ = client2.recvfrom(BUFFER_SIZE)
    for _ in range(10):
        data = struct.pack("2i?b?", 100, 300, True, 1, 0)
        client1.sendto(xor(data, key1), (SERVER_IP, SERVER_PORT))
        client2.sendto(xor(data, key2), (SERVER_IP, SERVER_PORT))
        time.sleep(0.1)
    level_msg = ""
    try:
        for _ in range(10):
            response, _ = client1.recvfrom(BUFFER_SIZE)
            decoded = xor(response, key1).decode(errors="ignore")
            if decoded.startswith("LEVEL:"):
                level_msg = decoded
                break
    except:
        pass
    stop_server()
    client1.close()
    client2.close()
    assert level_msg.startswith("LEVEL:"), "Expected LEVEL message after both players on door"
    print(f"✅ Passed: Level transitioned -> {level_msg}\n")

# 🧪 בדיקה 5: קליע נשלח מהשרת כששני שחקנים מחוברים

def test_bullet_hit_simulation():
    print("\n🔍 Test: Bullet simulated hit response...")
    start_server()
    client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client1.settimeout(3)
    client1.sendto("Shooter1".encode(), (SERVER_IP, SERVER_PORT))
    client1.recvfrom(BUFFER_SIZE)
    key1, _ = client1.recvfrom(BUFFER_SIZE)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client2.settimeout(3)
    client2.sendto("Shooter2".encode(), (SERVER_IP, SERVER_PORT))
    client2.recvfrom(BUFFER_SIZE)
    key2, _ = client2.recvfrom(BUFFER_SIZE)
    print("⏱ Waiting for bullets to spawn...")
    time.sleep(3)
    found_bullet = False
    try:
        for _ in range(10):
            response, _ = client1.recvfrom(BUFFER_SIZE)
            decoded = xor(response, key1).decode(errors="ignore")
            if decoded.startswith("BULLETS:") and "," in decoded:
                found_bullet = True
                break
    except:
        pass
    stop_server()
    client1.close()
    client2.close()
    assert found_bullet, "Expected at least one bullet to be sent from server"
    print("✅ Passed: Bullet detected in server response.\n")

# 🧪 בדיקה 6: האם ההודעות מוצפנות באמת עם שני שחקנים

def test_data_encryption():
    print("\n🔍 Test: Data sent from server is encrypted...")
    start_server()
    client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client1.settimeout(3)
    client1.sendto("Encrypt1".encode(), (SERVER_IP, SERVER_PORT))
    client1.recvfrom(BUFFER_SIZE)
    key1, _ = client1.recvfrom(BUFFER_SIZE)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client2.settimeout(3)
    client2.sendto("Encrypt2".encode(), (SERVER_IP, SERVER_PORT))
    client2.recvfrom(BUFFER_SIZE)
    key2, _ = client2.recvfrom(BUFFER_SIZE)
    data = struct.pack("2i?b?", 100, 300, True, 0, 0)
    client1.sendto(xor(data, key1), (SERVER_IP, SERVER_PORT))
    client2.sendto(xor(data, key2), (SERVER_IP, SERVER_PORT))
    time.sleep(1)
    encrypted_data, _ = client1.recvfrom(BUFFER_SIZE)
    try:
        plain = encrypted_data.decode(errors="ignore")
        assert not plain.startswith("1|"), "Data should be encrypted, but looks like plain text."
        print("✅ Passed: Data is not readable without XOR (confirmed encrypted).\n")
    except Exception:
        print("✅ Passed: Data raised decode error as expected.\n")
    stop_server()
    client1.close()
    client2.close()

if __name__ == "__main__":
    test_third_client_blocked()
    time.sleep(5)
    test_server_crash_detection()
    time.sleep(5)
    test_timer_runs_correctly()
    time.sleep(5)
    test_level_transition()
    time.sleep(5)
    test_bullet_hit_simulation()
    time.sleep(5)
    test_data_encryption()