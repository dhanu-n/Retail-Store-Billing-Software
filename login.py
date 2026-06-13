from tkinter import *
from tkinter import messagebox
import mysql.connector
import subprocess
import sys
import logging
import os

# ================= LOGGING =================

log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_directory, "billing_app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ================= DATABASE =================

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="billingdb1"
    )
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username varchar(20) not null,
        password varchar(20) not null,
        role varchar(20) not null,
        user_id varchar(10) not null
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("""
        INSERT INTO users (username, password, role, user_id) VALUES
        ('Dhanu', 'admin', 'admin', 'BL_001'),
        ('Cash1', 'cash', 'cashier', 'BL_002'),
        ('Cash2', 'cash', 'cashier', 'BL_003')
        """)
        conn.commit()

except mysql.connector.Error as err:
    messagebox.showerror("Database Error", str(err))

# ================= MAIN WINDOW =================

root = Tk()
root.state("zoomed")
root.title("Billing Software - Login")
root.resizable(True, False)

Username_var = StringVar()
Password_var = StringVar()
show_pass = BooleanVar()

# ================= CANVAS =================

canvas = Canvas(root)
canvas.pack(fill=BOTH, expand=True)

# ================= LOGIN CARD =================

Card = Frame(root, bg="#f0eaf8", padx=40, pady=30)

card_window = canvas.create_window(
    0, 0,
    window=Card,
    width=360,
    height=360
)

def center_card():
    canvas.coords(
        card_window,
        root.winfo_width() // 2,
        root.winfo_height() // 2
    )

# ================= FOOTER =================

footer_text = canvas.create_text(
    0, 0,
    text="Developed by Dhanu - 2026",
    fill="black",
    font=("arial", 9),
    tags="footer"
)

# ================= GRADIENT BACKGROUND =================

def draw_gradient(event=None):
    canvas.delete("gradient")

    width = root.winfo_width()
    height = root.winfo_height()

    r1, g1, b1 = 0xa8, 0xc8, 0xe8
    r2, g2, b2 = 0xe8, 0xb4, 0xc8

    for i in range(height):
        r = int(r1 + (r2 - r1) * i / height)
        g = int(g1 + (g2 - g1) * i / height)
        b = int(b1 + (b2 - b1) * i / height)

        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

    center_card()

    canvas.coords(
        footer_text,
        width // 2,
        height - 50
    )

    canvas.tag_raise("footer")

# ================= BANNER =================

canvas.create_text(
    0, 60,
    text="RETAIL STORE",
    fill="black",
    font=("times new roman", 25, "bold")
)

canvas.create_text(
    0, 100,
    text="BILLING MANAGEMENT SYSTEM",
    fill="black",
    font=("times new roman", 19)
)

# ================= LOGIN UI =================

Label(Card, text="LOGIN", bg="#f0eaf8", fg="black",
      font=("times new roman", 22, "bold")).pack(pady=(0, 5))

Label(Card, text="Enter your credentials to continue",
      bg="#f0eaf8", fg="black",
      font=("arial", 10)).pack(pady=(0, 20))

Label(Card, text="Username",
      bg="#f0eaf8", fg="black",
      font=("arial", 11, "bold"), anchor="w").pack(fill=X)

username_entry = Entry(Card, textvariable=Username_var,
                       font=("arial", 13), bd=2,
                       relief=GROOVE, bg="white")
username_entry.pack(fill=X, pady=(3, 15), ipady=6)

Label(Card, text="Password",
      bg="#f0eaf8", fg="black",
      font=("arial", 11, "bold"), anchor="w").pack(fill=X)

password_entry = Entry(Card, textvariable=Password_var,
                       font=("arial", 13), bd=2,
                       relief=GROOVE, show="*",
                       bg="white")
password_entry.pack(fill=X, pady=(3, 5), ipady=6)

Checkbutton(Card, text="Show Password",
            variable=show_pass,
            bg="#f0eaf8",
            font=("arial", 9),
            command=lambda: password_entry.config(
                show="" if show_pass.get() else "*")
            ).pack(anchor="w", pady=(0, 20))

# ================= USER CLASS =================

class User:
    def __init__(self, username, role, user_id):
        self.username = username
        self.role = role
        self.user_id = user_id

    def get_details(self):
        return f"{self.username} - {self.role} - {self.user_id}"

# ================= LOGIN FUNCTION =================

def login():
    uname = Username_var.get().strip()
    pwd = Password_var.get().strip()

    if uname == "" or pwd == "":
        messagebox.showerror("Error", "Please enter Username and Password!")
        return

    try:
        cursor.execute(
            "SELECT user_id, role FROM users WHERE username=%s AND password=%s",
            (uname, pwd)
        )
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            role = result[1]

            user = User(uname, role, user_id)

            logger.info(f"Login Successful | {user.get_details()}")

            messagebox.showinfo("Login Successful", f"Welcome {uname}!")

            root.destroy()
            subprocess.Popen([sys.executable, "billing.py", role, user_id])

        else:
            logger.warning(f"Login Failed | {uname}")
            messagebox.showerror("Login Failed", "Invalid Username or Password!")
            Password_var.set("")

    except mysql.connector.Error as err:
        logger.error(f"Database Error: {err}")
        messagebox.showerror("Database Error", str(err))

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        messagebox.showerror("Error", "Something went wrong!")

# ================= LOGIN BUTTON =================

Button(Card, text="LOGIN", command=login,
       bg="grey", fg="black",
       font=("arial", 13, "bold"),
       bd=0, pady=10, cursor="hand2").pack(fill=X)

# ================= EVENTS =================

root.bind("<Return>", lambda e: login())
username_entry.focus()

root.bind("<Configure>", draw_gradient)

# run safely after UI loads
root.after(100, draw_gradient)

center_card()

# ================= START APP =================

root.mainloop()
