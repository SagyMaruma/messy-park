import sys
import socket
import struct
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

# Open path for every file, in this case I need the client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from client.game_client import run_game

class ServerConnectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect...")
        self.setGeometry(100, 100, 400, 250)
        self.center_window()
        self.init_ui()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.label = QLabel("Enter IP Address:", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 14, QFont.Bold))
        self.label.setStyleSheet("color: #333;")
        layout.addWidget(self.label)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("E.g., 127.0.0.1")
        self.ip_input.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 10px; background-color: #fff; border: 2px solid #FF7F32;")
        layout.addWidget(self.ip_input)

        self.name_label = QLabel("Name:", self)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.label.setStyleSheet("color: #333;")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Your Name")
        self.name_input.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 10px; background-color: #fff; border: 2px solid #FF7F32;")
        layout.addWidget(self.name_input)

        self.connect_button = QPushButton(" Connect", self)
        self.connect_button.setStyleSheet("font-size: 16px; background-color: #FF7F32; color: white; padding: 12px; border-radius: 10px; font-weight: bold;")
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #f9f9f9; border-radius: 15px;")

    def connect_to_server(self):
        ip_address = self.ip_input.text().strip()
        player_name = self.name_input.text().strip()
        if not ip_address:
            self.label.setText("Enter a valid IP Address!")
            return
        if not player_name:
            self.label.setText("Enter a valid name!")
            return
        self.start_client(ip_address, player_name)

    def start_client(self, ip_address, player_name):
        self.client_window = ClientWindow(ip_address, player_name)
        self.client_window.show()
        self.close()

class ClientWindow(QWidget):
    def __init__(self, ip_address, player_name):
        super().__init__()
        self.ip_address = ip_address
        self.player_name = player_name
        self.setWindowTitle("Info")
        self.setGeometry(100, 100, 800, 600)
        self.center_window()
        self.init_ui()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Connected successfully! How was the game?", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 18, QFont.Bold))
        self.label.setStyleSheet("color: #333;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.connect_to_game_server()

    def connect_to_game_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip_address, 5555))
            player_id = struct.unpack("i", self.client_socket.recv(4))[0]
            self.role = "Fire" if player_id == 1 else "Water"
            name_data = self.player_name.encode().ljust(20)
            self.client_socket.sendall(name_data)
            self.start_game(player_id)
        except Exception as e:
            self.label.setText(f"Not connected: {str(e)}")

    def start_game(self, player_id):
        run_game(player_id, self.client_socket)
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerConnectionWindow()
    window.show()
    sys.exit(app.exec_())