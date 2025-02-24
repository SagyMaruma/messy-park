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
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

# Open path for evry file in this case I need the client.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from client.game_client import run_game


class ServerConnectionWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("coneect...")
        self.setGeometry(0, 0, 350, 200)
        self.center_window()
        self.init_ui()

    def center_window(self):
        # open the window  in the center of the screen.
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # text for the IP.
        self.label = QLabel("Enter IP address:", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: black;")
        layout.addWidget(self.label)

        # text box(where the IP address is.)
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("For Example: 127.0.0.1")
        self.ip_input.setStyleSheet(
            "font-size: 16px; padding: 10px; border-radius: 8px; background-color: white; border: 2px solid #FF7F00;"
        )
        layout.addWidget(self.ip_input)

        # text for the name.
        self.label = QLabel("Name:", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: black;")
        layout.addWidget(self.label)
        # text box(where the Name address is). still needed to be fixed later need to make it a variable and sent to the server after login.
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("example: sagy")
        self.name_input.setStyleSheet(
            "font-size: 16px; padding: 10px; border-radius: 8px; background-color: white; border: 2px solid #FF7F00;"
        )
        layout.addWidget(self.name_input)

        # login button.
        self.connect_button = QPushButton("Login", self)
        self.connect_button.setStyleSheet(
            "font-size: 16px; background-color: #FF7F00; color: white; padding: 12px; border-radius: 8px;"
        )
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #f4f4f4;")  # background color.

    def connect_to_server(self):
        ip_address = self.ip_input.text().strip()
        if ip_address:
            self.start_client(ip_address)
        else:
            self.label.setText("Enter IP address:")

    def start_client(self, ip_address):
        # conect to the server and start the client.
        self.client_window = ClientWindow(ip_address)
        self.client_window.show()
        self.close()


class ClientWindow(QWidget):
    # window that shows you the id of the player.
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address
        self.setWindowTitle("Info")
        self.setGeometry(0, 0, 800, 600)
        self.center_window()
        self.init_ui()

    def center_window(self):
        # open the window in the center.
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        # Gui design style.
        self.label = QLabel(f"connected successfully how was the game? good...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; color: black;")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.label)

        self.connect_to_game_server()

    def connect_to_game_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(
                (self.ip_address, 5555)
            )  # connect to the IP server.

            # get id player from the server.
            player_id = struct.unpack("i", self.client_socket.recv(4))[0]

            # start the fun start_game that start the client.
            self.start_game(player_id)

        except Exception as e:
            self.label.setText(f"not coneccted to the server: {str(e)}")

    def start_game(self, player_id):
        # login been successful
        run_game(player_id, self.client_socket)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ServerConnectionWindow()
    window.show()

    sys.exit(app.exec_())
