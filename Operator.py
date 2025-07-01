import sys, csv
import oracledb
from datetime import datetime
from PyQt5.QtWidgets import (
QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
QFormLayout, QFileDialog, QComboBox 
)
from PyQt5.QtCore import Qt
from Login import LoginWindow  


# Oracle Client Setup
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")
conn = oracledb.connect(user="Project", password="1234", dsn="localhost:1521/XE")

class OperatorWindow(QWidget):
    def __init__(self, linked_id):
        super().__init__()
        self.linked_id = linked_id
        self.setWindowTitle("Operator Dashboard")
        self.resize(1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QTabWidget::pane {
                background: #ffffff;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #87ceeb;
                border: 1px solid #4682b4;
                padding: 10px;
                margin: 2px;
                border-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #1e90ff;
                color: white;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #32cd32;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #228b22;
            }
            QLabel {
                font-size: 15px;
            }
            QTableWidget {
                border: 1px solid #ccc;
                background-color: #ffffff;
            }
        """)
        export_csv_button = QPushButton("Export CSV")
        export_csv_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)


        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tabs)

        # Tabs
        self.add_user_tab = QWidget()
        self.view_users_tab = QWidget()
        self.toll_history_tab = QWidget()
        self.maintenance_tab = QWidget()
        self.salary_tab = QWidget()
        self.profile_tab = QWidget()
        self.export_tab = QWidget()

        self.tabs.addTab(self.add_user_tab, "Add User")
        self.tabs.addTab(self.view_users_tab, "Manage Users")
        self.tabs.addTab(self.toll_history_tab, "Toll History")
        self.tabs.addTab(self.maintenance_tab, "Maintenance")
        self.tabs.addTab(self.salary_tab, "Salary Info")
        self.tabs.addTab(self.profile_tab, "My Profile")
        self.tabs.addTab(self.export_tab, "Export CSV")

        self.init_add_user()
        self.init_view_users()
        self.init_toll_history()
        self.init_maintenance()
        self.init_salary_info()
        self.init_profile_tab()
        self.init_export_tab()

        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)

    def logout(self):
        self.close()
        QMessageBox.information(self, "Logout", "You have been logged out.")
        self.login_window = LoginWindow()
        self.login_window.show()


    def init_add_user(self):
        layout = QFormLayout(self.add_user_tab)
        self.new_user_name = QLineEdit()
        self.new_user_contact = QLineEdit()
        self.new_user_balance = QLineEdit()
        self.new_user_username = QLineEdit()

        self.vehicle_number_input = QLineEdit()
        self.vehicle_number_input.setPlaceholderText("e.g., DHA-1234")

        self.vehicle_type_dropdown = QComboBox()
        self.vehicle_type_dropdown.addItems(["Car", "Truck", "Bus", "Bike"])

        btn = QPushButton("Register User")
        btn.clicked.connect(self.add_user)

        layout.addRow("Name:", self.new_user_name)
        layout.addRow("Contact:", self.new_user_contact)
        layout.addRow("Balance:", self.new_user_balance)
        layout.addRow("Username:", self.new_user_username)
        layout.addRow("Vehicle Number:", self.vehicle_number_input)
        layout.addRow("Vehicle Type:", self.vehicle_type_dropdown)
        layout.addRow(btn)


    def add_user(self):
        name = self.new_user_name.text().strip()
        contact = self.new_user_contact.text().strip()
        balance = self.new_user_balance.text().strip()
        username = self.new_user_username.text().strip()
        vehicle_number = self.vehicle_number_input.text().strip()
        vehicle_type = self.vehicle_type_dropdown.currentText()
        if not name or not balance.isdigit() or not username:
            QMessageBox.warning(self, "Input Error", "Please enter valid Name, Balance, and Username.")
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM USERS_LOGIN WHERE USERNAME = :1", (username,))
            if cur.fetchone()[0] > 0:
                QMessageBox.warning(self, "Duplicate Username", f"The username '{username}' already exists. Please choose another.")
                cur.close()
                return

            cur.execute("SELECT NVL(MAX(U_ID), 0) + 1 FROM USERS")
            uid = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO USERS (U_ID, U_NAME, U_CONTACT, BALANCE, O_ID)
                VALUES (:1, :2, :3, :4, :5)
            """, (uid, name, contact, int(balance), self.linked_id))

            cur.execute("SELECT NVL(MAX(LOGIN_ID), 0) + 1 FROM USERS_LOGIN")
            lid = cur.fetchone()[0]
            pwd = f"user{uid}"

            cur.execute("""
                INSERT INTO USERS_LOGIN (LOGIN_ID, USERNAME, PASSWORD, ROLE, LINKED_ID)
                VALUES (:1, :2, :3, 'User', :4)
            """, (lid, username, pwd, uid))

            # Add vehicle
            if vehicle_number:
                cur.execute("SELECT NVL(MAX(V_ID), 0) + 1 FROM VEHICLE")
                vid = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO VEHICLE (V_ID, VEHICLE_TYPE, V_NUMBER, U_ID)
                    VALUES (:1, :2, :3, :4)
                """, (vid, vehicle_type, vehicle_number, uid))

            conn.commit()
            cur.close()

            QMessageBox.information(self, "Success", f"User registered successfully!\nAuto-generated Password: {pwd}")
            self.new_user_name.clear()
            self.new_user_contact.clear()
            self.new_user_balance.clear()
            self.new_user_username.clear()
            self.vehicle_number_input.clear()
            self.load_user_list()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", str(e))

    def init_view_users(self):
        layout = QVBoxLayout(self.view_users_tab)
        self.user_table = QTableWidget()
        layout.addWidget(QLabel("Registered Users"))
        layout.addWidget(self.user_table)
        self.user_table.cellDoubleClicked.connect(self.confirm_delete_user)
        self.load_user_list()

    def load_user_list(self):
        cur = conn.cursor()
        cur.execute("SELECT U_ID, U_NAME, U_CONTACT, BALANCE FROM USERS WHERE O_ID=:1", (self.linked_id,))
        rows = cur.fetchall()
        self.user_table.setRowCount(len(rows))
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["U_ID", "Name", "Contact", "Balance"])
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.user_table.setItem(r, c, QTableWidgetItem(str(val)))
        cur.close()

    def confirm_delete_user(self, row, col):
        uid = int(self.user_table.item(row, 0).text())
        uname = self.user_table.item(row, 1).text()
        reply = QMessageBox.question(self, "Delete User",
            f"Are you sure you want to delete user '{uname}' (U_ID: {uid})?\n"
            "This will also remove their vehicles and toll history.",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                cur = conn.cursor()
                # Delete tolls first
                cur.execute("DELETE FROM TOLL_PAYMENT WHERE V_ID IN (SELECT V_ID FROM VEHICLE WHERE U_ID = :1)", (uid,))
                # Delete vehicles
                cur.execute("DELETE FROM VEHICLE WHERE U_ID = :1", (uid,))
                # Delete login
                cur.execute("DELETE FROM USERS_LOGIN WHERE LINKED_ID = :1 AND ROLE = 'User'", (uid,))
                # Delete user
                cur.execute("DELETE FROM USERS WHERE U_ID = :1", (uid,))
                conn.commit()
                cur.close()
                QMessageBox.information(self, "Deleted", f"User {uname} and related data deleted.")
                self.load_user_list()
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "Error", str(e))

    def init_toll_history(self):
        layout = QVBoxLayout(self.toll_history_tab)
        self.toll_table = QTableWidget()
        layout.addWidget(QLabel("Toll Payments"))
        layout.addWidget(self.toll_table)
        self.load_toll_history()

    def load_toll_history(self):
        cur = conn.cursor()
        cur.execute("""
            SELECT TP.P_ID, V.U_ID, TP.BOOTHLOCATION, TP.AMOUNT, TP.DATETIME
            FROM TOLL_PAYMENT TP
            JOIN VEHICLE V ON TP.V_ID=V.V_ID
            WHERE V.U_ID IN (SELECT U_ID FROM USERS WHERE O_ID=:1)
            ORDER BY TP.DATETIME DESC
        """, (self.linked_id,))
        rows = cur.fetchall()
        self.toll_table.setRowCount(len(rows))
        self.toll_table.setColumnCount(5)
        self.toll_table.setHorizontalHeaderLabels(["P_ID", "U_ID", "Booth", "Amount", "Date"])
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.toll_table.setItem(r, c, QTableWidgetItem(str(val)))
        cur.close()

    def init_maintenance(self):
        layout = QFormLayout(self.maintenance_tab)
        self.maint_desc = QLineEdit()
        btn = QPushButton("Log Maintenance")
        btn.clicked.connect(self.log_maintenance)
        layout.addRow("Description:", self.maint_desc)
        layout.addRow(btn)

    def log_maintenance(self):
        desc = self.maint_desc.text().strip()
        if not desc:
            QMessageBox.warning(self, "Error", "Enter description")
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT NVL(MAX(M_ID),0)+1 FROM MAINTENACE")
            mid = cur.fetchone()[0]
            now = datetime.now().strftime("%d-%b-%y")
            cur.execute("""
                INSERT INTO MAINTENACE(M_ID, DESCRIPTION, O_ID, DATETIME)
                VALUES(:1, :2, :3, TO_DATE(:4,'DD-MON-YY'))
                """, (mid, desc, self.linked_id, now))

            conn.commit()
            cur.close()
            QMessageBox.information(self, "Logged", "Maintenance recorded")
            self.maint_desc.clear()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", str(e))

    def init_salary_info(self):
        layout = QVBoxLayout(self.salary_tab)
        self.salary_label = QLabel()
        layout.addWidget(self.salary_label)
        self.load_salary_info()

    def load_salary_info(self):
        cur = conn.cursor()
        cur.execute("SELECT SALARY, O_CONTACT FROM OPERATOR WHERE O_ID=:1", (self.linked_id,))
        row = cur.fetchone() or (0, 'N/A')
        salary, contact = row
        today = datetime.today()
        nxt = datetime(today.year + (today.month // 12), (today.month % 12) + 1, 1)
        days = (nxt - today).days
        self.salary_label.setText(f"<b>Salary:</b> ৳{salary}<br><b>Contact:</b> {contact}<br><b>Days to next pay:</b> {days}")
        cur.close()

    def init_profile_tab(self):
        layout = QFormLayout(self.profile_tab)
        cur = conn.cursor()
        cur.execute("SELECT O_NAME, O_CONTACT, SHIFT_START, SHIFT_END FROM OPERATOR WHERE O_ID=:1", (self.linked_id,))
        o = cur.fetchone() or ("N/A", "N/A", "N/A", "N/A")
        cur.close()
        for label, val in zip(["Name:", "Contact:", "Shift Start:", "Shift End:"], o):
            layout.addRow(label, QLabel(f"<b>{val}</b>"))

    def init_export_tab(self):
        layout = QVBoxLayout(self.export_tab)

        b1 = QPushButton("Export User List to CSV")
        b1.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        b2 = QPushButton("Export Toll History to CSV")
        b2.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        b1.clicked.connect(self.export_users_csv)
        b2.clicked.connect(self.export_toll_csv)

        layout.addWidget(b1)
        layout.addWidget(b2)


    def export_users_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save User List CSV", "", "*.csv")
        if not path: return
        cur = conn.cursor()
        cur.execute("SELECT U_ID, U_NAME, U_CONTACT, BALANCE FROM USERS WHERE O_ID=:1", (self.linked_id,))
        rows = cur.fetchall(); cur.close()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["U_ID", "Name", "Contact", "Balance"])
            writer.writerows(rows)
        QMessageBox.information(self, "Exported", f"Saved to {path}")

    def export_toll_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Toll History CSV", "", "*.csv")
        if not path: return
        cur = conn.cursor()
        cur.execute("""
            SELECT TP.P_ID, V.U_ID, TP.BOOTHLOCATION, TP.AMOUNT, TP.DATETIME
            FROM TOLL_PAYMENT TP
            JOIN VEHICLE V ON TP.V_ID=V.V_ID
            WHERE V.U_ID IN (SELECT U_ID FROM USERS WHERE O_ID=:1)
        """, (self.linked_id,))
        rows = cur.fetchall(); cur.close()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["P_ID", "U_ID", "Booth", "Amount", "Date"])
            writer.writerows(rows)
        QMessageBox.information(self, "Exported", f"Saved to {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OperatorWindow(linked_id=1)
    win.show()
    sys.exit(app.exec_())