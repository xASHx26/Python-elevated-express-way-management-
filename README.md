# 🛣️ Python Elevated Expressway Management using PyQt and Oracle 10g

A desktop-based elevated expressway toll management system built with Python (PyQt5) and Oracle 10g. This system manages user registration, toll payments, vehicle tracking, maintenance records, recharges, and salary details — all within a modern graphical interface

---

## 👥 Roles Supported
 
| Role      | Responsibilities                                                                 |
|-----------|-----------------------------------------------------------------------------------|
| 🔑 Admin     | (Optional) System-wide control panel (not mandatory)                             |
| 👨‍💼 Manager  | Monitor booth income, operator profiles, salaries, and maintenance logs         |
| 👷 Operator | Register users and vehicles, manage user data, monitor toll payments, export data |
| 🚗 User     | Pay tolls, recharge balance, and view transaction history                        |

---

## 🧰 Tech Stack

- 💻 Python 3.8+
- 🎨 PyQt5 for GUI
- 🗄️ Oracle 10g Express Edition (XE)
- 🧱 Oracle Instant Client (e.g., 23.8)

---

## 📁 Project Structure


---

## ⚙️ Setup Instructions

### 1️⃣ Install Oracle 10g

Download and install Oracle 10g Express Edition from:
👉 https://www.oracle.com/database/technologies/xe-downloads.html

2️⃣ Install Oracle Instant Client
Download from:
👉 https://www.oracle.com/database/technologies/instant-client.html

Extract to:C:\oracle\instantclient_23_8
Reference this in your Python code:oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")

3️⃣ Install Required Python Packages
Install using pip:pip install -r requirements.txt

requirements.txt:
PyQt5
oracledb

🧩 Features Summary
🚗 User
View real-time balance

Pay toll based on vehicle type

Recharge via bKash, Nagad, Rocket, Card, Bank

View transaction & toll history

👷 Operator
Register users and vehicles

Auto-generate user credentials

View and delete users with confirmation

View toll payments by users

Export users and toll history to CSV

Log maintenance descriptions

👨‍💼 Manager
View booth toll summary

Manage salary information

Oversee operator activity and maintenance logs

🗂️ Tables Used
USERS

USERS_LOGIN

VEHICLE

VEHICLE_TYPE_TOLL

TOLL_PAYMENT

TRANSACTION_HISTORY

RECHARGE

OPERATOR

MANAGER

MAINTENACE

Also includes sequences:

TOLL_SEQ

TRANS_HIST_SEQ

RECHARGE_SEQ

etc.

🛡️ Security Note
Passwords are currently stored in plain text (for demo purposes). For production, consider encrypting passwords and adding session management.

Tables:
-- MANAGER table
CREATE TABLE MANAGER (
  M_ID         NUMBER PRIMARY KEY,
  M_NAME       VARCHAR2(100),
  M_CONTACT    VARCHAR2(20)
);

-- OPERATOR table
CREATE TABLE OPERATOR (
  O_ID         NUMBER PRIMARY KEY,
  O_NAME       VARCHAR2(100),
  O_CONTACT    VARCHAR2(20),
  SHIFT_START  VARCHAR2(20),
  SHIFT_END    VARCHAR2(20),
  SALARY       NUMBER,
  M_ID         NUMBER REFERENCES MANAGER(M_ID)
);

-- USERS table
CREATE TABLE USERS (
  U_ID     NUMBER PRIMARY KEY,
  U_NAME   VARCHAR2(100),
  U_CONTACT VARCHAR2(20),
  BALANCE  NUMBER,
  O_ID     NUMBER REFERENCES OPERATOR(O_ID)
);

-- USERS_LOGIN table
CREATE TABLE USERS_LOGIN (
  LOGIN_ID   NUMBER PRIMARY KEY,
  USERNAME   VARCHAR2(50) UNIQUE,
  PASSWORD   VARCHAR2(50),
  ROLE       VARCHAR2(20),
  LINKED_ID  NUMBER
);

-- VEHICLE table
CREATE TABLE VEHICLE (
  V_ID          NUMBER PRIMARY KEY,
  VEHICLE_TYPE  VARCHAR2(20),
  V_NUMBER      VARCHAR2(20),
  U_ID          NUMBER REFERENCES USERS(U_ID)
);

-- VEHICLE_TYPE_TOLL table
CREATE TABLE VEHICLE_TYPE_TOLL (
  VEHICLE_TYPE  VARCHAR2(20) PRIMARY KEY,
  TOLL_AMOUNT   NUMBER
);

-- TOLL_PAYMENT table
CREATE TABLE TOLL_PAYMENT (
  P_ID          NUMBER PRIMARY KEY,
  V_ID          NUMBER REFERENCES VEHICLE(V_ID),
  BOOTHLOCATION VARCHAR2(50),
  AMOUNT        NUMBER,
  DATETIME      DATE
);

-- TRANSACTION_HISTORY table
CREATE TABLE TRANSACTION_HISTORY (
  T_ID      NUMBER PRIMARY KEY,
  U_ID      NUMBER REFERENCES USERS(U_ID),
  TYPE      VARCHAR2(20), -- 'Recharge' or 'Payment'
  AMOUNT    NUMBER,
  DATETIME  DATE
);

-- RECHARGE table
CREATE TABLE RECHARGE (
  R_ID            NUMBER PRIMARY KEY,
  U_ID            NUMBER REFERENCES USERS(U_ID),
  AMOUNT          NUMBER,
  PAYMENT_METHOD  VARCHAR2(20),
  DATETIME        DATE
);

-- MAINTENACE table
CREATE TABLE MAINTENACE (
  M_ID       NUMBER PRIMARY KEY,
  DESCRIPTION VARCHAR2(200),
  O_ID        NUMBER REFERENCES OPERATOR(O_ID),
  DATETIME    DATE
);

-- SEQUENCES
CREATE SEQUENCE TOLL_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE RECHARGE_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE TRANS_HIST_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE USER_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE LOGIN_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE VEHICLE_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE MAINT_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE MANAGER_SEQ START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE OPERATOR_SEQ START WITH 1 INCREMENT BY 1;

-- Sample Toll Amounts
INSERT INTO VEHICLE_TYPE_TOLL (VEHICLE_TYPE, TOLL_AMOUNT) VALUES ('Car', 50);
INSERT INTO VEHICLE_TYPE_TOLL (VEHICLE_TYPE, TOLL_AMOUNT) VALUES ('Truck', 100);
INSERT INTO VEHICLE_TYPE_TOLL (VEHICLE_TYPE, TOLL_AMOUNT) VALUES ('Bus', 80);
INSERT INTO VEHICLE_TYPE_TOLL (VEHICLE_TYPE, TOLL_AMOUNT) VALUES ('Bike', 20);
