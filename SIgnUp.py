import sys
import oracledb
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)

# Oracle Instant Client setup
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")

# DB Connection
conn = oracledb.connect(user="Project", password="1234", dsn="localhost:1521/XE")

class SignUpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Signup")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Contact Number")

        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("Initial Balance")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self.handle_signup)

        layout.addWidget(QLabel("Full Name"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Contact Number"))
        layout.addWidget(self.contact_input)
        layout.addWidget(QLabel("Initial Balance"))
        layout.addWidget(self.balance_input)
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def handle_signup(self):
        name = self.name_input.text().strip()
        contact = self.contact_input.text().strip()
        balance_text = self.balance_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not all([name, contact, balance_text, username, password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return
        if not balance_text.isdigit() or int(balance_text) < 0:
            QMessageBox.warning(self, "Input Error", "Balance must be a non-negative number.")
            return

        balance = int(balance_text)

        cursor = conn.cursor()
        try:
            # Check for username duplication
            cursor.execute("SELECT COUNT(*) FROM USERS_LOGIN WHERE USERNAME = :1", (username,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Error", "Username already taken.")
                return

           
            user_id_var = cursor.var(int)
            cursor.execute("""
                INSERT INTO USERS (U_ID, U_NAME, U_CONTACT, BALANCE)
                VALUES (USERS_SEQ.NEXTVAL, :1, :2, :3)
                RETURNING U_ID INTO :4
            """, (name, contact, balance, user_id_var))
            user_id = user_id_var.getvalue()[0]

           
            login_id_var = cursor.var(int)
            cursor.execute("""
                INSERT INTO USERS_LOGIN (LOGIN_ID, USERNAME, PASSWORD, ROLE, LINKED_ID)
                VALUES (USERS_LOGIN_SEQ.NEXTVAL, :1, :2, 'User', :3)
                RETURNING LOGIN_ID INTO :4
            """, (username, password, user_id, login_id_var))

            conn.commit()
            QMessageBox.information(self, "Success", f"User registered successfully!\nYour User ID is {user_id}.")
            self.clear_fields()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            cursor.close()

    def clear_fields(self):
        self.name_input.clear()
        self.contact_input.clear()
        self.balance_input.clear()
        self.username_input.clear()
        self.password_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignUpWindow()
    window.show()
    sys.exit(app.exec_())
