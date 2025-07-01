import sys
import oracledb
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QFormLayout, QTimeEdit, QHeaderView
)
from PyQt5.QtCore import QTime
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from Login import LoginWindow

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")
conn = oracledb.connect(user="Project", password="1234", dsn="localhost:1521/XE")

class ManagerWindow(QWidget):
    def get_manager_name(self):
        cursor = conn.cursor()
        cursor.execute("SELECT M_NAME FROM MANAGER WHERE M_ID = :1", (self.linked_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else f"Manager #{self.linked_id}"

    def __init__(self, linked_id):
        super().__init__()
        self.linked_id = linked_id
        self.setWindowTitle("Manager Dashboard")
        self.resize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4ff;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #aaa;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background: #a29bfe;
                color: white;
                padding: 10px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 6px;
            }
            QTabBar::tab:selected {
                background: #6c5ce7;
                font-weight: bold;
            }
            QLineEdit, QTimeEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #00b894;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #019875;
            }
            QPushButton#logout {
                background-color: #e74c3c;
                font-weight: bold;
            }
            QPushButton#logout:hover {
                background-color: #c0392b;
            }
            QLabel {
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #ccc;
                background-color: #ffffff;
            }
        """)

        layout = QVBoxLayout()
        self.setLayout(layout)

        top_bar = QHBoxLayout()
        welcome = QLabel(f"Welcome, {self.get_manager_name()}")

        welcome.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d3436;")
        top_bar.addWidget(welcome)
        top_bar.addStretch()

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setObjectName("logout")
        self.logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(self.logout_btn)

        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.operator_tab = QWidget()
        self.add_operator_tab = QWidget()
        self.maintenance_tab = QWidget()
        self.income_tab = QWidget()

        self.tabs.addTab(self.operator_tab, "Operator List")
        self.tabs.addTab(self.add_operator_tab, "Add Operator")
        self.tabs.addTab(self.maintenance_tab, "Maintenance Logs")
        self.tabs.addTab(self.income_tab, "Income Report")

        self.init_operator_list()
        self.init_add_operator()
        self.init_maintenance_logs()
        self.init_income_report()

    def logout(self):
        QMessageBox.information(self, "Logged Out", "You have logged out.")
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def init_operator_list(self):
        layout = QVBoxLayout()
        self.operator_table = QTableWidget()
        self.operator_table.cellDoubleClicked.connect(self.confirm_delete_operator)
        layout.addWidget(QLabel("Operators under you"))
        layout.addWidget(self.operator_table)
        self.operator_tab.setLayout(layout)
        self.load_operator_data()

    def load_operator_data(self):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT O_ID, O_NAME, O_CONTACT, SALARY, SHIFT_START, SHIFT_END
            FROM OPERATOR WHERE M_ID = :1
        """, (self.linked_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        self.operator_table.setColumnCount(len(columns))
        self.operator_table.setHorizontalHeaderLabels(columns)
        self.operator_table.setRowCount(len(rows))
        self.operator_table.horizontalHeader().setStretchLastSection(True)
        self.operator_table.horizontalHeader().setStyleSheet("font-weight: bold; background-color: #dfe6e9;")
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.operator_table.setItem(r, c, QTableWidgetItem(str(val)))
        cursor.close()

    def confirm_delete_operator(self, row, column):
        oid = self.operator_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Delete Operator", f"Are you sure you want to delete Operator ID {oid}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_operator(int(oid))

    def delete_operator(self, oid):
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM USERS_LOGIN WHERE LINKED_ID = :1 AND ROLE = 'Operator'", (oid,))
            cursor.execute("DELETE FROM OPERATOR WHERE O_ID = :1 AND M_ID = :2", (oid, self.linked_id))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Deleted", f"Operator ID {oid} deleted successfully.")
            self.load_operator_data()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", str(e))

    def init_add_operator(self):
        layout = QFormLayout()

        self.op_name_input = QLineEdit()
        self.op_contact_input = QLineEdit()
        self.salary_input = QLineEdit()
        self.shift_start_input = QTimeEdit()
        self.shift_start_input.setDisplayFormat("HH:mm")
        self.shift_start_input.setTime(QTime(9, 0))
        self.shift_end_input = QTimeEdit()
        self.shift_end_input.setDisplayFormat("HH:mm")
        self.shift_end_input.setTime(QTime(17, 0))
        self.username_input = QLineEdit()

        self.add_op_button = QPushButton("Add Operator")
        self.add_op_button.clicked.connect(self.insert_operator)

        layout.addRow("Operator Name:", self.op_name_input)
        layout.addRow("Phone Number:", self.op_contact_input)
        layout.addRow("Salary:", self.salary_input)
        layout.addRow("Shift Start:", self.shift_start_input)
        layout.addRow("Shift End:", self.shift_end_input)
        layout.addRow("Username:", self.username_input)
        layout.addWidget(self.add_op_button)

        self.add_operator_tab.setLayout(layout)

    def insert_operator(self):
        name = self.op_name_input.text().strip()
        contact = self.op_contact_input.text().strip()
        salary = self.salary_input.text().strip()
        shift_start = self.shift_start_input.time().toString("HH:mm")
        shift_end = self.shift_end_input.time().toString("HH:mm")
        username = self.username_input.text().strip()

        if not (name and contact and salary.isdigit() and shift_start and shift_end and username):
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT NVL(MAX(O_ID), 0) + 1 FROM OPERATOR")
            next_oid = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO OPERATOR (O_ID, O_NAME, O_CONTACT, M_ID, SALARY, SHIFT_START, SHIFT_END)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (next_oid, name, contact, self.linked_id, int(salary), shift_start, shift_end))
            cursor.execute("SELECT NVL(MAX(LOGIN_ID), 0) + 1 FROM USERS_LOGIN")
            next_login_id = cursor.fetchone()[0]
            password = f"op{next_oid}"
            cursor.execute("""
                INSERT INTO USERS_LOGIN (LOGIN_ID, USERNAME, PASSWORD, ROLE, LINKED_ID)
                VALUES (:1, :2, :3, 'Operator', :4)
            """, (next_login_id, username, password, next_oid))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Operator {name} added.\nUsername: {username}, Password: {password}")
            self.op_name_input.clear()
            self.op_contact_input.clear()
            self.salary_input.clear()
            self.shift_start_input.setTime(QTime(9, 0))
            self.shift_end_input.setTime(QTime(17, 0))
            self.username_input.clear()
            self.load_operator_data()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))

    def init_maintenance_logs(self):
        layout = QVBoxLayout()
        self.maint_table = QTableWidget()
        layout.addWidget(QLabel("Maintenance by your Operators"))
        layout.addWidget(self.maint_table)
        self.maintenance_tab.setLayout(layout)
        self.load_maintenance_logs()

    def load_maintenance_logs(self):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT M.M_ID, M.DESCRIPTION, M.O_ID, M.DATETIME
            FROM MAINTENACE M
            JOIN OPERATOR O ON M.O_ID = O.O_ID
            WHERE O.M_ID = :1
        """, (self.linked_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        self.maint_table.setColumnCount(len(columns))
        self.maint_table.setHorizontalHeaderLabels(columns)
        self.maint_table.setRowCount(len(rows))
        self.maint_table.horizontalHeader().setStretchLastSection(True)
        self.maint_table.horizontalHeader().setStyleSheet("font-weight: bold; background-color: #dfe6e9;")
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.maint_table.setItem(r, c, QTableWidgetItem(str(val)))
        cursor.close()

    def init_income_report(self):
        layout = QVBoxLayout()
        self.income_label = QLabel("Calculating income...")
        self.income_label.setStyleSheet("font-size: 18px; font-weight: bold; color: darkblue;")
        layout.addWidget(self.income_label)
        self.income_tab.setLayout(layout)
        self.calculate_income()

    def calculate_income(self):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT NVL(SUM(TP.AMOUNT), 0)
            FROM TOLL_PAYMENT TP
            JOIN VEHICLE V ON TP.V_ID = V.V_ID
            JOIN USERS U ON V.U_ID = U.U_ID
            JOIN OPERATOR O ON U.O_ID = O.O_ID
            WHERE O.M_ID = :1
        """, (self.linked_id,))
        total_toll = cursor.fetchone()[0]
        cursor.execute("SELECT NVL(SUM(SALARY), 0) FROM OPERATOR WHERE M_ID = :1", (self.linked_id,))
        total_salary = cursor.fetchone()[0]
        cursor.execute("""
            SELECT NVL(COUNT(*), 0)
            FROM MAINTENACE M
            JOIN OPERATOR O ON M.O_ID = O.O_ID
            WHERE O.M_ID = :1
        """, (self.linked_id,))
        total_maint = cursor.fetchone()[0]
        income = total_toll - total_salary - total_maint
        self.income_label.setText(
            f"Total Toll: ৳{total_toll}  |  Salary: ৳{total_salary}  |  Maintenance Count: {total_maint}\nNet Income: ৳{income}"
        )
        cursor.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManagerWindow(linked_id=1)
    window.show()
    sys.exit(app.exec_())
