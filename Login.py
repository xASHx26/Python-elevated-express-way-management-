import sys
import oracledb
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)


oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")


conn = oracledb.connect(
    user="Project",
    password="1234",
    dsn="localhost:1521/XE"
)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(300, 180)

       
        layout = QVBoxLayout()

       
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        cursor = conn.cursor()
        cursor.execute("""
            SELECT ROLE, LINKED_ID 
            FROM USERS_LOGIN 
            WHERE USERNAME = :1 AND PASSWORD = :2
        """, (username, password))
        result = cursor.fetchone()
        cursor.close()

        if result:
            role, linked_id = result
            QMessageBox.information(self, "Success", f"Welcome {role}!")
            self.hide()
            self.redirect_user(role, linked_id)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def redirect_user(self, role, linked_id):
        if role == "Manager":
            from Manager import ManagerWindow
            self.window = ManagerWindow(linked_id)
        elif role == "Admin":
            from Admin import AdminWindow
            self.window = AdminWindow()
        elif role == "Operator":
            from Operator import OperatorWindow
            self.window = OperatorWindow(linked_id)
        elif role == "User":
            from User import UserWindow
            self.window = UserWindow(linked_id)
        else:
            QMessageBox.critical(self, "Error", "Unknown role.")
            return

        self.window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
