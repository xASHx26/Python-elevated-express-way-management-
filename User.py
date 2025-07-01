import sys
import oracledb
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from Login import LoginWindow

# Correct database credentials
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")
try:
    conn = oracledb.connect(user="Project", password="1234", dsn="localhost:1521/XE")
except oracledb.DatabaseError as e:
    print("Database connection failed:", e)
    sys.exit(1)

class UserWindow(QWidget):
    def __init__(self, linked_id):
        super().__init__()
        self.linked_id = linked_id
        self.setWindowTitle("User Dashboard")
        self.resize(900, 680)

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 12pt;
                background-color: #f0f4f7;
            }
            QTableWidget {
                border: 1px solid #ccc;
                gridline-color: #ddd;
                background-color: white;
            }
            QLabel {
                color: #333;
            }
        """)

        main_layout = QVBoxLayout(self)

        nav_bar = QFrame()
        nav_bar.setStyleSheet("background-color: #007BFF; padding: 12px; border-bottom: 2px solid #0056b3;")
        nav_layout = QHBoxLayout(nav_bar)

        self.name_label = QLabel("Name: Loading...")
        self.name_label.setStyleSheet("color: white; font-weight: bold;")
        self.balance_label = QLabel("Balance: Loading...")
        self.balance_label.setStyleSheet("color: white; font-weight: bold;")
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 6px 14px; border-radius: 5px;")
        logout_btn.clicked.connect(self.logout)

        nav_layout.addWidget(logout_btn, alignment=Qt.AlignLeft)
        nav_layout.addSpacing(30)
        nav_layout.addWidget(self.name_label)
        nav_layout.addSpacing(30)
        nav_layout.addWidget(self.balance_label)
        nav_layout.addStretch()
        main_layout.addWidget(nav_bar)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border-top: 2px solid #007BFF; background-color: #ffffff; }
            QTabBar::tab {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                padding: 10px;
                margin-right: 4px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: bold;
                color: #007BFF;
            }
        """)

        self.transaction_tab = QWidget()
        self.toll_tab = QWidget()
        self.recharge_tab = QWidget()

        self.tabs.addTab(self.transaction_tab, "Transaction History")
        self.tabs.addTab(self.toll_tab, "Toll History ")
        self.tabs.addTab(self.recharge_tab, "Recharge")

        main_layout.addWidget(self.tabs)

        self.init_transaction_tab()
        self.init_toll_tab()
        self.init_recharge_tab()
        self.load_user_info()

    def logout(self):
        QMessageBox.information(self, "Logged Out", "You have logged out.")
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


    def load_user_info(self):
        cur = conn.cursor()
        cur.execute("SELECT U_NAME, BALANCE FROM USERS WHERE U_ID = :1", (self.linked_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            name, balance = row
            self.name_label.setText(f"Name: {name}")
            self.balance_label.setText(f"Balance: {balance} ৳")

    def init_transaction_tab(self):
        layout = QVBoxLayout()
        self.transaction_table = QTableWidget()
        layout.addWidget(self.transaction_table)
        self.transaction_tab.setLayout(layout)
        self.load_transaction_history()

    def load_transaction_history(self):
        cur = conn.cursor()
        cur.execute("SELECT T_ID, TYPE, AMOUNT, DATETIME FROM TRANSACTION_HISTORY WHERE U_ID = :1 ORDER BY DATETIME DESC", (self.linked_id,))
        rows = cur.fetchall()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["T_ID", "Type", "Amount", "Date"])
        self.transaction_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.transaction_table.setItem(r, c, QTableWidgetItem(str(val)))
        cur.close()

    def init_toll_tab(self):
        layout = QVBoxLayout()
        self.toll_table = QTableWidget()
        self.toll_table.setStyleSheet("font-size: 12px;")
        layout.addWidget(QLabel("Toll Payment History"))
        layout.addWidget(self.toll_table)

        form_frame = QWidget()
        form_layout = QHBoxLayout()
        form_frame.setStyleSheet("background-color: #f2f2f2; border: 1px solid #ccc; padding: 10px;")
        form_frame.setLayout(form_layout)

        self.vehicle_dropdown = QComboBox()
        self.vehicle_dropdown.setStyleSheet("padding: 5px; font-size: 14px;")
        self.booth_input = QLineEdit()
        self.booth_input.setPlaceholderText("Enter Booth Location")
        self.booth_input.setStyleSheet("padding: 5px; font-size: 14px;")
        self.pay_btn = QPushButton("Pay Toll")
        self.pay_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF; 
                color: white; 
                padding: 8px 16px; 
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.pay_btn.clicked.connect(self.pay_toll)

        form_layout.addWidget(QLabel("Vehicle:"))
        form_layout.addWidget(self.vehicle_dropdown)
        form_layout.addWidget(QLabel("Booth:"))
        form_layout.addWidget(self.booth_input)
        form_layout.addWidget(self.pay_btn)

        layout.addWidget(form_frame)
        self.toll_tab.setLayout(layout)

        self.load_vehicle_dropdown()
        self.load_toll_history()

    def load_vehicle_dropdown(self):
        self.vehicle_dropdown.clear()
        cur = conn.cursor()
        cur.execute("SELECT V_ID, V_NUMBER, VEHICLE_TYPE FROM VEHICLE WHERE U_ID = :1", (self.linked_id,))
        self.vehicles = cur.fetchall()
        for v_id, v_number, vtype in self.vehicles:
            self.vehicle_dropdown.addItem(f"{v_id} - {v_number} ({vtype})", (v_id, vtype))
        cur.close()


    def load_toll_history(self):
        cur = conn.cursor()
        cur.execute("""
            SELECT TP.P_ID, V.V_ID, V.VEHICLE_TYPE, TP.BOOTHLOCATION, TP.AMOUNT, TP.DATETIME
            FROM TOLL_PAYMENT TP
            JOIN VEHICLE V ON TP.V_ID = V.V_ID
            WHERE V.U_ID = :1
            ORDER BY TP.DATETIME DESC
        """, (self.linked_id,))
        rows = cur.fetchall()
        self.toll_table.setColumnCount(6)
        self.toll_table.setHorizontalHeaderLabels(["P_ID", "Vehicle ID", "Type", "Booth", "Amount", "Date"])
        self.toll_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.toll_table.setItem(r, c, QTableWidgetItem(str(val)))
        cur.close()

    def pay_toll(self):
        if self.vehicle_dropdown.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "No vehicle selected.")
            return

        booth = self.booth_input.text().strip()
        if not booth:
            QMessageBox.warning(self, "Error", "Enter booth location.")
            return

        v_id, vtype = self.vehicle_dropdown.currentData()
        cur = conn.cursor()
        cur.execute("SELECT TOLL_AMOUNT FROM VEHICLE_TYPE_TOLL WHERE VEHICLE_TYPE = :1", (vtype,))
        result = cur.fetchone()
        if not result:
            QMessageBox.warning(self, "Error", f"No toll configured for vehicle type {vtype}")
            cur.close()
            return
        toll_amount = result[0]

        cur.execute("SELECT BALANCE FROM USERS WHERE U_ID = :1", (self.linked_id,))
        balance = cur.fetchone()[0]
        if balance < toll_amount:
            QMessageBox.warning(self, "Error", "Insufficient balance.")
            cur.close()
            return

        now = datetime.now().strftime("%d-%b-%y %H:%M:%S")
        try:
            cur.execute("SELECT TOLL_SEQ.NEXTVAL FROM dual")
            p_id = cur.fetchone()[0]
            cur.execute("SELECT TRANS_HIST_SEQ.NEXTVAL FROM dual")
            t_id = cur.fetchone()[0]

            cur.execute("UPDATE USERS SET BALANCE = BALANCE - :1 WHERE U_ID = :2", (toll_amount, self.linked_id))
            cur.execute("""
                INSERT INTO TOLL_PAYMENT (P_ID, V_ID, BOOTHLOCATION, AMOUNT, DATETIME)
                VALUES (:1, :2, :3, :4, TO_DATE(:5, 'DD-MON-YY HH24:MI:SS'))
            """, (p_id, v_id, booth, toll_amount, now))

            cur.execute("""
                INSERT INTO TRANSACTION_HISTORY (T_ID, U_ID, TYPE, AMOUNT, DATETIME)
                VALUES (:1, :2, 'Payment', -:3, TO_DATE(:4, 'DD-MON-YY HH24:MI:SS'))
            """, (t_id, self.linked_id, toll_amount, now))

            conn.commit()
            QMessageBox.information(self, "Success", f"Toll paid: {toll_amount} ৳")
            self.booth_input.clear()
            self.load_user_info()
            self.load_toll_history()
            self.load_transaction_history()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            cur.close()

    def init_recharge_tab(self):
        layout = QVBoxLayout()
        form = QHBoxLayout()
        self.recharge_amount = QLineEdit()
        self.recharge_amount.setPlaceholderText("Enter amount")
        self.method_dropdown = QComboBox()
        self.method_dropdown.addItems(["bKash", "Rocket", "Nagad", "Card", "Bank"])
        btn = QPushButton("Recharge")
        btn.clicked.connect(self.handle_recharge)

        form.addWidget(QLabel("Amount:"))
        form.addWidget(self.recharge_amount)
        form.addWidget(QLabel("Method:"))
        form.addWidget(self.method_dropdown)
        form.addWidget(btn)

        layout.addLayout(form)
        self.recharge_table = QTableWidget()
        layout.addWidget(QLabel("Recharge History"))
        layout.addWidget(self.recharge_table)
        self.recharge_tab.setLayout(layout)

        self.load_recharge_history()

    def handle_recharge(self):
        amt_txt = self.recharge_amount.text().strip()
        if not amt_txt.isdigit() or int(amt_txt) <= 0:
            QMessageBox.warning(self, "Invalid", "Enter a valid amount.")
            return
        amount = int(amt_txt)
        method = self.method_dropdown.currentText()
        cur = conn.cursor()
        try:
            cur.execute("SELECT RECHARGE_SEQ.NEXTVAL FROM dual")
            r_id = cur.fetchone()[0]
            cur.execute("SELECT TRANS_HIST_SEQ.NEXTVAL FROM dual")
            t_id = cur.fetchone()[0]
            now = datetime.now().strftime("%d-%b-%y %H:%M:%S")

            cur.execute("UPDATE USERS SET BALANCE = BALANCE + :1 WHERE U_ID = :2", (amount, self.linked_id))
            cur.execute("""
                INSERT INTO RECHARGE (R_ID, U_ID, AMOUNT, PAYMENT_METHOD, DATETIME)
                VALUES (:1, :2, :3, :4, TO_DATE(:5, 'DD-MON-YY HH24:MI:SS'))
            """, (r_id, self.linked_id, amount, method, now))
            cur.execute("""
                INSERT INTO TRANSACTION_HISTORY (T_ID, U_ID, TYPE, AMOUNT, DATETIME)
                VALUES (:1, :2, 'Recharge', :3, TO_DATE(:4, 'DD-MON-YY HH24:MI:SS'))
            """, (t_id, self.linked_id, amount, now))

            conn.commit()
            QMessageBox.information(self, "Success", f"Recharged ৳{amount}")
            self.recharge_amount.clear()
            self.load_user_info()
            self.load_transaction_history()
            self.load_recharge_history()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            cur.close()

    def load_recharge_history(self):
        cur = conn.cursor()
        cur.execute("SELECT R_ID, AMOUNT, PAYMENT_METHOD, DATETIME FROM RECHARGE WHERE U_ID = :1 ORDER BY DATETIME DESC", (self.linked_id,))
        rows = cur.fetchall()
        self.recharge_table.setColumnCount(4)
        self.recharge_table.setHorizontalHeaderLabels(["R_ID", "Amount", "Method", "Date"])
        self.recharge_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.recharge_table.setItem(r, c, QTableWidgetItem(str(val)))
        cur.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = UserWindow(linked_id=1)
    win.show()
    sys.exit(app.exec_())
