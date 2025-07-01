import sys
import oracledb
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QTabWidget, QMessageBox, QHBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Login import LoginWindow

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")
conn = oracledb.connect(user="Project", password="1234", dsn="localhost:1521/XE")

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.resize(1000, 600)

        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
                font-size: 13px;
                background-color: #f5f7fa;
            }
            QListWidget {
                background: #e1eaff;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #4e88ff;
                color: white;
            }
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                margin-bottom: 4px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 4px 8px;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f2f2f2;
                border: 1px solid #ccc;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #4e88ff;
                color: white;
                padding: 6px;
                border: none;
            }
        """)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.currentRowChanged.connect(self.display_table)
        main_layout.addWidget(self.sidebar)

        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout)

        top_bar = QHBoxLayout()
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        top_bar.addStretch()
        top_bar.addWidget(self.logout_btn)
        center_layout.addLayout(top_bar)

        self.stacked_widget = QStackedWidget()
        center_layout.addWidget(self.stacked_widget)

        self.tables = {
            "USERS_LOGIN": "SELECT LOGIN_ID, USERNAME, ROLE, LINKED_ID FROM USERS_LOGIN",
            "MANAGER": "SELECT * FROM MANAGER",
            "OPERATOR": "SELECT * FROM OPERATOR",
            "USERS": "SELECT * FROM USERS",
            "VEHICLE_TYPE_TOLL": "SELECT * FROM VEHICLE_TYPE_TOLL",
            "VEHICLE": "SELECT * FROM VEHICLE",
            "TOLL_PAYMENT": "SELECT * FROM TOLL_PAYMENT",
            "RECHARGE": "SELECT * FROM RECHARGE",
            "TRANSACTION_HISTORY": "SELECT * FROM TRANSACTION_HISTORY",
            "MAINTENACE": "SELECT * FROM MAINTENACE"
        }

        self.table_widgets = {}

        for table_name, query in self.tables.items():
            self.sidebar.addItem(table_name)
            table = QTableWidget()
            table.setAlternatingRowColors(True)
            self.stacked_widget.addWidget(table)
            self.table_widgets[table_name] = (table, query)

        self.load_all_tables()
        self.sidebar.setCurrentRow(0)

    def display_table(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def load_all_tables(self):
        for table_name, (widget, query) in self.table_widgets.items():
            self.load_table_data(widget, query)

    def load_table_data(self, table_widget, query):
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            table_widget.setRowCount(len(rows))
            table_widget.setColumnCount(len(columns))
            table_widget.setHorizontalHeaderLabels(columns)

            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            table_widget.resizeColumnsToContents()
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error loading data", str(e))

    def logout(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AdminWindow()
    win.show()
    sys.exit(app.exec_())
