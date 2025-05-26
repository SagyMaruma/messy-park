import os
import socket
from PyQt6.QtWidgets import QWidget,QApplication,QVBoxLayout,QLabel,QLineEdit,QPushButton,QHBoxLayout
import sys
from client import main
from threading import Thread


class LoginWindow(QWidget):
    server_running = False
    new_game=None
    server_thread = None
    def __init__(self):
        super().__init__()
        self.setGeometry(100,200,300,400)
        self.setWindowTitle("My Game")

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        name_lbl = QLabel("Please enter your name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name")

        ip_lbl = QLabel("Please enter the server ip address:")
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("ip")

        create_server_btn = QPushButton("Create a server")
        create_server_btn.clicked.connect(self.create_server)

        join_server_btn = QPushButton("Enter a server")
        join_server_btn.clicked.connect(self.join_server)

        btn_layout.addWidget(join_server_btn)
        btn_layout.addWidget(create_server_btn)

        main_layout.addWidget(name_lbl)
        main_layout.addWidget(self.name_edit)
        main_layout.addWidget(ip_lbl)
        main_layout.addWidget(self.ip_edit)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        

        self.setStyleSheet("""
               QLabel{
                        color:red;
                    }           

            """)

    def create_server(self):
        if not self.server_thread or not self.server_thread.is_alive:
            path_to_server = 'py ./server/server.py'
            self.server_thread = Thread(target=os.system,args= (path_to_server,))
            print("starting game server....")
            self.server_thread.start()
            self.local_ip = get_local_ip()
            print(f"game server running on {self.local_ip}")
            self.ip_edit.setText(self.local_ip)

            self.join_server()
    
    def join_server(self):
        name = self.name_edit.text().strip()
        ip = self.ip_edit.text().strip()
        if name and ip:
            main(name,ip)
        return


def get_local_ip():
    try:
        # Open a dummy connection to a public address (no data is sent)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Use a public IP like Google's DNS
        ip = s.getsockname()[0]     # This gives the local IP used to reach out
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # Fallback if something fails



if __name__ == "__main__":
    app=QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    app.exec()
