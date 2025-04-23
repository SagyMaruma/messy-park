import json
import socket
import struct
import threading
import time
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["fire_water_game"]

# Game state
player_positions = {1: (0, 0), 2: (0, 0)}
player_names = ["Fireboy", "Watergirl"]
player_roles = {1: "Fire", 2: "Water"}
player_animations = {1: {"facing_right": True, "walk_frame": 0}, 2: {"facing_right": True, "walk_frame": 0}}
player_approvals = {1: False, 2: False}  # Approval for next level
current_level = 1
clients = {}

def start_server():
    """start the game server"""

    # create tcp socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", 5555))
    tcp_socket.listen(2)
    print("tcp socket listening on port 5555...")

    # create udp socket
    udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0",5556))
    print("udp socket listening on port 5556...")

    player_id = 1
    while player_id <= 2:
        client_socket, client_address = tcp_socket.accept()
        print(f"Player {player_id} ({player_roles[player_id]}) connected from {client_address}")
        clients[player_id] = client_socket
        client_socket.send(player_id)
        threading.Thread(target=handle_secondary, args=(client_socket,player_id)).start()
        player_id += 1

    # create a udp thread
    threading.Thread(target=handle_player_data, daemon=True, args=(udp_socket,clients[1].gethostname(),clients[2].gethostname()))


def handle_player_data(udp_socket:socket.socket,addr1,addr2):
    while True:
        data,addr = udp_socket.recvfrom()
        if addr == addr1:
            udp_socket.sendto(data,addr2)
        else:
            udp_socket.sendto(data,addr1)


def handle_secondary(client_socket: socket.socket,player_id):
    while True:
        raw_data = client_socket.recv(1024)
        try:
            data = json.loads(raw_data.decode())

            match data.get("action", ""):
                case "new player":
                    new_player_connect(client_socket, data.get("data", ""))
                case "approval":
                    player_approvals.update({player_id:True})
                    if all(approval for _,approval in player_approvals):
                        current_level+=1
                        player_approvals.update({1:False,2:False})
                case _:
                    print("client sent an invalid action")

        except Exception as e:
            print(
                f"error occured while handling a tcp request from ({client_socket.getpeername}):{e})"
            )

def new_player_connect(socket,player_data):
    return



if __name__ == "__main__":
    start_server()
