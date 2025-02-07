import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFont, QPixmap, QIcon  # Import QIcon


class GameWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Game Login")
        self.setGeometry(
            100, 100, 500, 300
        )  # Larger window size for the game-like interface

        # Set a custom window icon
        self.setWindowIcon(
            QIcon("player_still.png")
        )  # Replace 'icon.png' with the path to your image file

        # Set background color
        self.setStyleSheet(
            "background-color: #FFFFFF;"
        )  # White background for a clean, bright look

        # Main Layout
        main_layout = QVBoxLayout()

        # Add pixel font and style for headings and inputs
        font = QFont("Arial", 14, QFont.Bold)
        input_font = QFont("Arial", 16, QFont.Bold)

        # Title
        title_label = QLabel("Game Login", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #FF7F32;")  # Orange color

        # Player Name Input
        self.name_label = QLabel("Enter your Name:", self)
        self.name_label.setFont(font)
        self.name_label.setStyleSheet("color: #FF7F32;")  # Orange color for labels

        self.name_input = QLineEdit(self)
        self.name_input.setFont(input_font)
        self.name_input.setStyleSheet(
            """
            background-color: #FFEBDB;  # Light orange background
            color: #333333;
            border: 2px solid #FF7F32;
            border-radius: 10px;
            padding: 10px;
        """
        )
        self.name_input.setPlaceholderText("Enter your name")

        # Server IP Address Input
        self.server_label = QLabel("Enter Server IP", self)
        self.server_label.setAlignment(Qt.AlignCenter)
        self.server_label.setFont(font)
        self.server_label.setStyleSheet("color: #FF7F32;")  # Orange color for labels

        self.server_input = QLineEdit(self)
        self.server_input.setFont(input_font)
        self.server_input.setStyleSheet(
            """
            background-color: #FFEBDB;  # Light orange background
            color: #333333;
            border: 2px solid #FF7F32;
            border-radius: 10px;
            padding: 10px;
        """
        )
        self.server_input.setPlaceholderText("Enter server IP address")

        # Login Button
        self.login_button = QPushButton("Login", self)
        self.login_button.setFont(QFont("Arial", 18, QFont.Bold))
        self.login_button.setStyleSheet(
            """
            background-color: #FF7F32;
            color: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            font-weight: bold;
        """
        )
        self.login_button.clicked.connect(self.login)

        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(self.server_label)
        main_layout.addWidget(self.server_input)
        main_layout.addWidget(self.login_button)

        # Set main layout
        self.setLayout(main_layout)

    def login(self):
        # Get input values
        name = self.name_input.text()
        server_ip = self.server_input.text()

        # Simple validation
        if not name:
            print("Error: Please enter a name!")
            return

        if not server_ip:
            print("Error: Please enter a valid server IP address!")
            return

        # Save values as variables
        player_name = name
        server_ip_address = server_ip

        # מדפיס את המשתנים בעזרת ה בעתיד נעביר אותם אל השרת את  השם
        print(f"Player Name: {player_name}")
        print(f"Server IP: {server_ip_address}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())
