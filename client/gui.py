# gui.py

import os
import socket
from time import sleep
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
import sys
from threading import Thread

from client import main  # קריאה לפונקציה הראשית של המשחק


class LoginWindow(QWidget):
    server_running = False
    new_game = None
    server_thread = None

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 200, 320, 420)
        self.setWindowTitle("Fireboy & Watergirl Multiplayer")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(18)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        title_lbl = QLabel("🔥💧 Welcome to the Game 💧🔥")
        title_lbl.setObjectName("TitleLabel")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_lbl = QLabel("Enter your name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name")

        ip_lbl = QLabel("Enter server IP address:")
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("Server IP")

        join_server_btn = QPushButton("Join Server")
        join_server_btn.setObjectName("BlueButton")
        join_server_btn.clicked.connect(self.join_server)

        create_server_btn = QPushButton("Create Server")
        create_server_btn.setObjectName("RedButton")
        create_server_btn.clicked.connect(self.create_server)

        btn_layout.addWidget(join_server_btn)
        btn_layout.addWidget(create_server_btn)

        main_layout.addWidget(title_lbl)
        main_layout.addSpacing(10)
        main_layout.addWidget(name_lbl)
        main_layout.addWidget(self.name_edit)
        main_layout.addWidget(ip_lbl)
        main_layout.addWidget(self.ip_edit)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }

            QLabel {
                color: #eeeeee;
            }

            #TitleLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 12px;
            }

            QLineEdit {
                background-color: #2e2e40;
                color: #ffffff;
                border: 1px solid #44475a;
                padding: 6px;
                border-radius: 6px;
            }

            QLineEdit:focus {
                border: 1px solid #61afef;
                background-color: #3b3b5b;
            }

            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }

            #RedButton {
                background-color: #d94f4f;
            }

            #RedButton:hover {
                background-color: #ff5c5c;
            }

            #RedButton:pressed {
                background-color: #a63a3a;
            }

            #BlueButton {
                background-color: #3b84d6;
            }

            #BlueButton:hover {
                background-color: #5a9df0;
            }

            #BlueButton:pressed {
                background-color: #2b6cb0;
            }
        """)

    def create_server(self):
        if not self.server_thread or not self.server_thread.is_alive():
            path_to_server = 'py ./server/server.py'
            self.server_thread = Thread(target=os.system, args=(path_to_server,))
            print("Starting game server...")
            self.server_thread.start()
            self.local_ip = get_local_ip()
            print(f"Game server running on {self.local_ip}")
            self.ip_edit.setText(self.local_ip)
            sleep(1)
            self.join_server()

    def join_server(self):
        name = self.name_edit.text().strip()
        ip = self.ip_edit.text().strip()
        if name and ip:
            main(name, ip)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    app.exec()
