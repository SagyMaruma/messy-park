import socket
import threading
import struct

# שמירה על מצב המשחק
player_positions = {1: (0, 0), 2: (0, 0), 3: (0, 0)}

def broadcast_positions(clients):
    """
    שולח לכל השחקנים את המיקומים של כולם.
    """
    for client_socket in clients.values():
        if client_socket:
            data = struct.pack(
                "6i", 
                *player_positions[1], 
                *player_positions[2], 
                *player_positions[3]
            )
            client_socket.sendall(data)

def handle_client(client_socket, player_id, clients):
    """
    מטפל בכל לקוח ומעדכן את המיקום שלו.
    """
    try:
        while True:
            # קבלת המיקום מהלקוח (שולח 3 ערכים: player_id, x, y)
            data = client_socket.recv(12)  # 12 בתים ל-3 מספרים שלמים
            if not data:
                break
            
            # פירוק הנתונים
            received_id, x, y = struct.unpack("3i", data)
            
            # וידוא שהעדכון מתאים לשחקן הנכון
            if received_id == player_id:
                player_positions[player_id] = (x, y)
                print(f"Player {player_id} updated position to: {x}, {y}")
                
                # שידור המיקומים לכל השחקנים
                broadcast_positions(clients)
    except Exception as e:
        print(f"Error with player {player_id}: {e}")
    finally:
        client_socket.close()
        del clients[player_id]

def main():
    """
    פונקציית השרת הראשית.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(3)
    print("Server listening on port 5555...")

    clients = {}
    player_id = 1

    while player_id <= 3:
        client_socket, client_address = server.accept()
        print(f"Player {player_id} connected from {client_address}")

        # שליחת מזהה השחקן ללקוח
        client_socket.sendall(struct.pack("i", player_id))

        # שמירת הלקוח ברשימת הלקוחות
        clients[player_id] = client_socket

        # יצירת חוט לטיפול בלקוח
        threading.Thread(target=handle_client, args=(client_socket, player_id, clients)).start()
        player_id += 1

if __name__ == "__main__":
    main()
