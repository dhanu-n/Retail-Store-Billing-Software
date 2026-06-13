from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import sys
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import datetime
import os
import logging

# Configure logging
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_directory, "billing_app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ================= ACCESS GUARD =================

if len(sys.argv) < 3:
    root = Tk()
    root.withdraw()
    messagebox.showerror("Access Denied", "Please login first to access the billing system.")
    sys.exit()

current_role = sys.argv[1]
current_user_id = sys.argv[2]

if current_role not in ["admin", "cashier"]:
    root = Tk()
    root.withdraw()
    messagebox.showerror("Access Denied", "Invalid role. Please login properly.")
    sys.exit()

# ================= DATABASE CONNECTION =================

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="billingdb1"
    )
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flexible_bills (
        bill_no INT AUTO_INCREMENT PRIMARY KEY,
        customer_name VARCHAR(100),
        phone_no VARCHAR(20),
        total_cosmetics FLOAT,
        total_grocery FLOAT,
        total_others FLOAT,
        tax_cosmetics FLOAT,
        tax_grocery FLOAT,
        tax_others FLOAT,
        grand_total FLOAT,
        biller_id VARCHAR(20),
        bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (biller_id) REFERENCES users(user_id)
    )
    """)
    conn.commit()

except mysql.connector.Error as err:
    messagebox.showerror("Database Error", str(err))

# ================= MAIN WINDOW =================

root = Tk()
root.geometry("1350x700")
root.title(f"Billing Software")
root.config(bg="#a8c8e8")

# ================= SCROLLABLE SETUP =================

main_canvas = Canvas(root, bg="#a8c8e8")

scrollbar_y = Scrollbar(root, orient=VERTICAL, command=main_canvas.yview)
scrollbar_x = Scrollbar(root, orient=HORIZONTAL, command=main_canvas.xview)

main_canvas.configure(
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set
)

scrollbar_y.pack(side=RIGHT, fill=Y)
scrollbar_x.pack(side=BOTTOM, fill=X)
main_canvas.pack(side=LEFT, fill=BOTH, expand=True)

# IMPORTANT: Frame inside canvas
main_frame = Frame(main_canvas, bg="#a8c8e8", width=1600, height=750)
main_frame.pack_propagate(False)

canvas_window = main_canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)

# ================= SCROLL REGION UPDATE =================

def update_scrollregion(event=None):
    main_canvas.update_idletasks()
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

main_frame.bind("<Configure>", update_scrollregion)

# ================= MOUSE SCROLL (VERTICAL) =================

def on_mousewheel(event):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

main_canvas.bind_all("<MouseWheel>", on_mousewheel)

# ================= HORIZONTAL SCROLL (SHIFT + SCROLL) =================

def on_shift_mousewheel(event):
    main_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind("<Shift-MouseWheel>", on_shift_mousewheel)

# ================= VARIABLES =================

c_name = StringVar()
c_phone = StringVar()

# ================= VALIDATION FUNCTIONS =================

def validate_name(value):
    if all(c.isalnum() or c.isspace() for c in value) or value == "":
        return True
    return False

def validate_numeric(value):
    if value.isdigit() or value == "":
        return True
    return False

def validate_phone(value):
    if (value.isdigit() or value == "") and len(value) <= 10:
        return True
    return False

name_validator = root.register(validate_name)
numeric_validator = root.register(validate_numeric)
phone_validator = root.register(validate_phone)

bill_no = StringVar()

# cosmetics
soap = IntVar()
cream = IntVar()
facewash = IntVar()
spray = IntVar()
lotion = IntVar()

# grocery
rice = IntVar()
oil = IntVar()
daal = IntVar()
wheat = IntVar()
sugar = IntVar()

# others
maza = IntVar()
coke = IntVar()
frooti = IntVar()
nimkos = IntVar()
biscuits = IntVar()

# totals
cosmetic_price = StringVar()
grocery_price = StringVar()
other_price = StringVar()

cosmetic_tax = StringVar()
grocery_tax = StringVar()
other_tax = StringVar()

# ================= LOGOUT FUNCTION =================

def logout():
    confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
    if confirm:
        root.destroy()
        subprocess.Popen([sys.executable, "login.py"])

# ================= TITLE =================

title = Label(
    main_frame,
    text="Billing Software",
    bg="#a8c8e8",
    fg="black",
    font=("times new roman", 30, "bold"),
    pady=10
)
title.place(x=0, y=0, relwidth=1, height=75)

# ================= LOGOUT BUTTON TOP RIGHT =================

btn_top_logout = Button(
    main_frame,
    text="Logout",
    command=logout,
    bg="#c0392b",
    fg="black",
    font=("times new roman", 12, "bold"),
    bd=4,
    width=10
)
btn_top_logout.place(x=1330, y=18, height=40)

# ================= CUSTOMER FRAME =================

F1 = LabelFrame(
    main_frame,
    text="Customer Details",
    font=("times new roman", 15, "bold"),
    bg="#a8c8e8", fg="#1a1a4e"
)
F1.place(x=0, y=80, relwidth=1)

Label(F1, text="Customer Name", bg="#a8c8e8", fg="black",
      font=("times new roman", 18, "bold")).grid(row=0, column=0, padx=20, pady=5)

txtcname = Entry(F1, width=15, textvariable=c_name, font="arial 15", bd=7,
                 bg="white", fg="black",
                 validate="key", validatecommand=(name_validator, "%P"))
txtcname.grid(row=0, column=1, pady=5, padx=10)

Label(F1, text="Phone No", bg="#a8c8e8", fg="black",
      font=("times new roman", 18, "bold")).grid(row=0, column=2, padx=20, pady=5)

txtphone = Entry(F1, width=15, textvariable=c_phone, font="arial 15", bd=7,
                 bg="white", fg="black",
                 validate="key", validatecommand=(phone_validator, "%P"))
txtphone.grid(row=0, column=3, pady=5, padx=10)

cursor.execute("SELECT IFNULL(MAX(bill_no), 0) + 1 FROM flexible_bills")
bill_no.set(str(cursor.fetchone()[0]))

Label(F1, text="Bill No", bg="#a8c8e8", fg="black",
      font=("times new roman", 18, "bold")).grid(row=0, column=4, padx=20, pady=5)

Entry(F1, width=15, textvariable=bill_no, font="arial 15", bd=7,
      bg="white", fg="black",
      state="readonly").grid(row=0, column=5, pady=5, padx=10)

# ================= COSMETICS FRAME =================

F2 = LabelFrame(main_frame, text="Cosmetics", font=("times new roman", 15, "bold"),
                bg="#a8c8e8", fg="#1a1a4e")
F2.place(x=6, y=180, width=325, height=380)

Label(F2, text="Bath Soap", font=("times new roman", 16, "bold"),
      bg="#a8c8e8", fg="black").grid(row=0, column=0, pady=10, padx=10)
Entry(F2, width=10, textvariable=soap, font=("times new roman", 16, "bold"),
      bd=5, bg="white", fg="black",
      validate="key", validatecommand=(numeric_validator, "%P")).grid(row=0, column=1, pady=10, padx=10)

Label(F2, text="Face Cream", font=("times new roman", 16, "bold"),
      bg="#a8c8e8", fg="black").grid(row=1, column=0, pady=10, padx=10)
Entry(F2, width=10, textvariable=cream, font=("times new roman", 16, "bold"),
      bd=5, bg="white", fg="black",
      validate="key", validatecommand=(numeric_validator, "%P")).grid(row=1, column=1, pady=10, padx=10)

Label(F2, text="Face Wash", font=("times new roman", 16, "bold"),
      bg="#a8c8e8", fg="black").grid(row=2, column=0, pady=10, padx=10)
Entry(F2, width=10, textvariable=facewash, font=("times new roman", 16, "bold"),
      bd=5, bg="white", fg="black",
      validate="key", validatecommand=(numeric_validator, "%P")).grid(row=2, column=1, pady=10, padx=10)

Label(F2, text="Hair Spray", font=("times new roman", 16, "bold"),
      bg="#a8c8e8", fg="black").grid(row=3, column=0, pady=10, padx=10)
Entry(F2, width=10, textvariable=spray, font=("times new roman", 16, "bold"),
      bd=5, bg="white", fg="black",
      validate="key", validatecommand=(numeric_validator, "%P")).grid(row=3, column=1, pady=10, padx=10)

Label(F2, text="Body Lotion", font=("times new roman", 16, "bold"),
      bg="#a8c8e8", fg="black").grid(row=4, column=0, pady=10, padx=10)
Entry(F2, width=10, textvariable=lotion, font=("times new roman", 16, "bold"),
      bd=5, bg="white", fg="black",
      validate="key", validatecommand=(numeric_validator, "%P")).grid(row=4, column=1, pady=10, padx=10)

# ================= GROCERY FRAME =================

F3 = LabelFrame(main_frame, text="Grocery", font=("times new roman", 15, "bold"),
                fg="#1a1a4e", bg="#a8c8e8")
F3.place(x=390, y=180, width=325, height=380)

items1 = [("Rice", rice), ("Food Oil", oil), ("Daal", daal),
          ("Wheat", wheat), ("Sugar", sugar)]

for i, (text, var) in enumerate(items1):
    Label(F3, text=text, font=("times new roman", 16, "bold"),
          bg="#a8c8e8", fg="black").grid(row=i, column=0, pady=10, padx=10)
    Entry(F3, width=10, textvariable=var, font=("times new roman", 16, "bold"),
          bd=5, bg="white", fg="black",
          validate="key", validatecommand=(numeric_validator, "%P")).grid(row=i, column=1, pady=10, padx=10)

# ================= OTHERS FRAME =================

F4 = LabelFrame(main_frame, text="Others", font=("times new roman", 15, "bold"),
                bg="#a8c8e8", fg="#1a1a4e")
F4.place(x=780, y=180, width=325, height=380)

items2 = [("Maza", maza), ("Coke", coke), ("Frooti", frooti),
          ("Nimkos", nimkos), ("Biscuits", biscuits)]

for i, (text, var) in enumerate(items2):
    Label(F4, text=text, font=("times new roman", 16, "bold"),
          bg="#a8c8e8", fg="black").grid(row=i, column=0, pady=10, padx=10)
    Entry(F4, width=10, textvariable=var, font=("times new roman", 16, "bold"),
          bd=5, bg="white", fg="black",
          validate="key", validatecommand=(numeric_validator, "%P")).grid(row=i, column=1, pady=10, padx=10)

# ================= BILL AREA =================

F5 = Frame(main_frame, bd=10, relief=GROOVE, bg="#f0eaf8")
F5.place(x=1150, y=180, width=370, height=400)

bill_title = Label(F5, text="Bill Area", font="arial 15 bold", bd=7,
                   relief=GROOVE, bg="#a8c8e8", fg="black")
bill_title.pack(fill=X)

scroll_y = Scrollbar(F5, orient=VERTICAL)
txtarea = Text(F5, yscrollcommand=scroll_y.set, bg="white", fg="black")
scroll_y.pack(side=RIGHT, fill=Y)
scroll_y.config(command=txtarea.yview)
txtarea.pack(fill=BOTH, expand=1)



# ================= OOP CLASSES =================

class Bill:
    def __init__(self, customer_name, phone, biller_id):
        self.customer_name = customer_name
        self.phone = phone
        self.biller_id = biller_id
        self.items = []

    def add_item(self, name, qty, price):
        self.items.append((name, qty, price))

    def calculate_total(self):
        return sum(qty * price for name, qty, price in self.items)
    
# ================= FUNCTIONS =================

def total():
    try:
        c_s_p = soap.get() * 40
        c_f_p = cream.get() * 140
        c_fw_p = facewash.get() * 240
        c_spr_p = spray.get() * 180
        c_l_p = lotion.get() * 260
        total_cos_price = c_s_p + c_f_p + c_fw_p + c_spr_p + c_l_p
        cosmetic_price.set("Rs. " + str(total_cos_price))
        cosmetic_tax.set("Rs. " + str(round(total_cos_price * 0.05)))

        g_r_p = rice.get() * 80
        g_f_o_p = oil.get() * 180
        g_d_p = daal.get() * 80
        g_w_p = wheat.get() * 60
        g_s_p = sugar.get() * 170
        total_groc_price = g_r_p + g_f_o_p + g_d_p + g_w_p + g_s_p
        grocery_price.set("Rs. " + str(total_groc_price))
        grocery_tax.set("Rs. " + str(round(total_groc_price * 0.05)))

        o_m_p = maza.get() * 50
        o_c_p = coke.get() * 60
        o_f_p = frooti.get() * 50
        o_n_p = nimkos.get() * 20
        o_b_p = biscuits.get() * 20
        total_other_price = o_m_p + o_c_p + o_f_p + o_n_p + o_b_p
        other_price.set("Rs. " + str(total_other_price))
        other_tax.set("Rs. " + str(round(total_other_price * 0.05)))
    except Exception as e:
      logger.error(f"Error in Total Calculation: {e}")
      messagebox.showerror("Error", "Error calculating totals")


    

def welcome_bill():
    txtarea.delete("1.0", END)
    txtarea.insert(END, "\t Welcome To Retail Store")
    txtarea.insert(END, f"\n\nBill No. : {bill_no.get()}")
    txtarea.insert(END, f"\nCustomer Name : {c_name.get()}")
    txtarea.insert(END, f"\nPhone No. : {c_phone.get()}")
    txtarea.insert(END, f"\nDate : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    txtarea.insert(END, f"\nBiller ID : {current_user_id}")
    txtarea.insert(END, "\n======================================")
    txtarea.insert(END, "\nProducts\t\tQTY\tPrice")
    txtarea.insert(END, "\n======================================")

def bill_area():
    total_bill = 0

    if c_name.get() == "" or c_phone.get() == "":
        messagebox.showerror("Error", "Customer Details Required")
        return
    bill = Bill(c_name.get(), c_phone.get(), current_user_id)

    welcome_bill()
    total()

    if soap.get() != 0:
        bill.add_item("Bath Soap", soap.get(), 40)
        txtarea.insert(END, f"\nBath Soap\t\t{soap.get()}\t{soap.get()*40}")
    if cream.get() != 0:
        bill.add_item("Face Cream", cream.get(), 140)
        txtarea.insert(END, f"\nFace Cream\t\t{cream.get()}\t{cream.get()*140}")
    if facewash.get() != 0:
        bill.add_item("Face Wash", facewash.get(), 240)
        txtarea.insert(END, f"\nFace Wash\t\t{facewash.get()}\t{facewash.get()*240}")
    if spray.get() != 0:
        bill.add_item("Hair Spray", spray.get(), 180)
        txtarea.insert(END, f"\nHair Spray\t\t{spray.get()}\t{spray.get()*180}")
    if lotion.get() != 0:
        bill.add_item("Body Lotion", lotion.get(), 260)
        txtarea.insert(END, f"\nBody Lotion\t\t{lotion.get()}\t{lotion.get()*260}")

    if rice.get() != 0:
        bill.add_item("Rice", rice.get(), 80)
        txtarea.insert(END, f"\nRice\t\t{rice.get()}\t{rice.get()*80}")
    if oil.get() != 0:
        bill.add_item("Food Oil", oil.get(), 180)
        txtarea.insert(END, f"\nFood Oil\t\t{oil.get()}\t{oil.get()*180}")
    if daal.get() != 0:
        bill.add_item("Daal", daal.get(), 80)
        txtarea.insert(END, f"\nDaal\t\t{daal.get()}\t{daal.get()*80}")
    if wheat.get() != 0:
        bill.add_item("Wheat", wheat.get(), 60)
        txtarea.insert(END, f"\nWheat\t\t{wheat.get()}\t{wheat.get()*60}")
    if sugar.get() != 0:
        bill.add_item("Sugar", sugar.get(), 170)
        txtarea.insert(END, f"\nSugar\t\t{sugar.get()}\t{sugar.get()*170}")

    if maza.get() != 0:
        bill.add_item("Maza", maza.get(), 50)
        txtarea.insert(END, f"\nMaza\t\t{maza.get()}\t{maza.get()*50}")
    if coke.get() != 0:
        bill.add_item("Coke", coke.get(), 60)
        txtarea.insert(END, f"\nCoke\t\t{coke.get()}\t{coke.get()*60}")
    if frooti.get() != 0:
        bill.add_item("Frooti", frooti.get(), 50)
        txtarea.insert(END, f"\nFrooti\t\t{frooti.get()}\t{frooti.get()*50}")
    if nimkos.get() != 0:
        bill.add_item("Nimkos", nimkos.get(), 20)
        txtarea.insert(END, f"\nNimkos\t\t{nimkos.get()}\t{nimkos.get()*20}")
    if biscuits.get() != 0:
        bill.add_item("Biscuits", biscuits.get(), 20)
        txtarea.insert(END, f"\nBiscuits\t\t{biscuits.get()}\t{biscuits.get()*20}")

    txtarea.insert(END, "\n======================================")

    total_bill = bill.calculate_total()
    txtarea.insert(END, "\n======================================")
    txtarea.insert(END, f"\nTotal Bill : Rs. {total_bill}")
    logger.info(
    f"Bill Generated | Customer: {c_name.get()} | Phone: {c_phone.get()} | "
    f"Biller: {current_user_id} | Total: {total_bill}"
)


def save_bill():
    try:
        if c_name.get() == "" or c_phone.get() == "":
            messagebox.showerror("Error", "Enter Customer Details First")
            return

        total()

        # ---- CALCULATE TOTALS ----
        t_cosmetics  = float(cosmetic_price.get().replace("Rs. ", ""))
        t_grocery    = float(grocery_price.get().replace("Rs. ", ""))
        t_others     = float(other_price.get().replace("Rs. ", ""))
        tx_cosmetics = float(cosmetic_tax.get().replace("Rs. ", ""))
        tx_grocery   = float(grocery_tax.get().replace("Rs. ", ""))
        tx_others    = float(other_tax.get().replace("Rs. ", ""))

        grand_total  = t_cosmetics + t_grocery + t_others + tx_cosmetics + tx_grocery + tx_others

        # ---- SQL ----
        sql = """
        INSERT INTO flexible_bills(
            customer_name, phone_no,
            total_cosmetics, total_grocery, total_others,
            tax_cosmetics, tax_grocery, tax_others,
            grand_total, biller_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            c_name.get(),
            c_phone.get(),
            t_cosmetics,
            t_grocery,
            t_others,
            tx_cosmetics,
            tx_grocery,
            tx_others,
            grand_total,
            current_user_id
        )

        # ---- DB EXECUTION ----
        cursor.execute(sql, values)
        conn.commit()

        generated_id = cursor.lastrowid
        bill_no.set(str(generated_id))

        logger.info(
            f"Bill Saved | Bill No: {generated_id} | Customer: {c_name.get()} | User: {current_user_id}"
        )

        messagebox.showinfo("Success", f"Bill Saved Successfully\nBill No: {generated_id}")

    except mysql.connector.Error as err:
        logger.error(f"DB Error in Save Bill: {err}")
        messagebox.showerror("Database Error", str(err))

    except Exception as e:
        logger.error(f"Unexpected Error in Save Bill: {e}")
        messagebox.showerror("Save Bill Error", str(e))


def clear_data():
    c_name.set("")
    c_phone.set("")
    cursor.execute("SELECT IFNULL(MAX(bill_no), 0) + 1 FROM flexible_bills")
    bill_no.set(str(cursor.fetchone()[0]))

    soap.set(0); cream.set(0); facewash.set(0); spray.set(0); lotion.set(0)
    rice.set(0); oil.set(0); daal.set(0); wheat.set(0); sugar.set(0)
    maza.set(0); coke.set(0); frooti.set(0); nimkos.set(0); biscuits.set(0)

    cosmetic_price.set(""); grocery_price.set(""); other_price.set("")
    cosmetic_tax.set(""); grocery_tax.set(""); other_tax.set("")
    txtarea.delete("1.0", END)

def generate_pdf():
    try:
        if txtarea.get("1.0", END).strip() == "":
            messagebox.showerror("Error", "No bill generated!")
            return

        # Fix — works on any computer
        folder = os.path.join(os.path.expanduser("~"), "Desktop", "Bills")
        os.makedirs(folder, exist_ok=True)
        pdf_file = os.path.join(folder, f"Bill_{bill_no.get()}.pdf")

        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="TitleStyle",
            parent=styles["Heading1"],
            fontSize=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a1a4e")
        )

        elements = [
            Paragraph("Retail Store - Billing Software", title_style),
            Spacer(1, 12)
        ]

        bill_text = txtarea.get("1.0", END).strip().split("\n")
        data = [line.split("\t") for line in bill_text]

        table = Table(data, colWidths=[3*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#a8c8e8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a1a4e")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f0eaf8")),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#1a1a4e"))
        ]))

        elements.append(table)
        doc.build(elements)

        logger.info(f"PDF Generated | Bill No: {bill_no.get()} | User: {current_user_id}")

        messagebox.showinfo("Success", f"PDF saved successfully!\n{os.path.abspath(pdf_file)}")

    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        messagebox.showerror("PDF Error", str(e))


def open_search():
    win = Toplevel(root)
    win.title("Search Bills")
    win.geometry("850x450")
    win.config(bg="#a8c8e8")

    search_var = StringVar()
    top = Frame(win, bg="#a8c8e8")
    top.pack(pady=10)

    Label(top, text="Customer/Bill No", bg="#a8c8e8", fg="black").pack(side=LEFT, padx=5)
    Entry(top, textvariable=search_var, width=30, bg="white", fg="black").pack(side=LEFT, padx=5)

    tree = ttk.Treeview(win, columns=("Bill", "Customer", "Phone", "Total"), show="headings")
    for col in ("Bill", "Customer", "Phone", "Total"):
        tree.heading(col, text=col)
    tree.pack(fill=BOTH, expand=True)

    def load_data():
        tree.delete(*tree.get_children())
        key = search_var.get()
        if key:
            cursor.execute("""
            SELECT bill_no, customer_name, phone_no, grand_total
            FROM flexible_bills
            WHERE customer_name LIKE %s OR bill_no LIKE %s
            """, (f"%{key}%", f"%{key}%"))
        else:
            cursor.execute("SELECT bill_no, customer_name, phone_no, grand_total FROM flexible_bills")
        for row in cursor.fetchall():
            tree.insert("", END, values=row)

    Button(top, text="Search", command=load_data,
           bg="#1a1a4e", fg="white").pack(side=LEFT, padx=5)
    load_data()


def open_streamlit_dashboard():
    subprocess.Popen(["streamlit", "run", "dashboard.py"])



# ================= BILL MENU FRAME =================

F6 = LabelFrame(main_frame, text="Bill Menu", font=("times new roman", 15, "bold"),
                fg="#1a1a4e", bg="#a8c8e8")
F6.place(x=0, y=560, relwidth=1, height=140)

Label(F6, text="Total Cosmetics", bg="#a8c8e8", fg="black",
      font=("times new roman", 14, "bold")).grid(row=0, column=0)
Entry(F6, width=18, textvariable=cosmetic_price, font="arial 10 bold",
      bd=7, bg="white", fg="black").grid(row=0, column=1)

Label(F6, text="Cosmetics Tax", bg="#a8c8e8", fg="black",
      font=("times new roman", 14, "bold")).grid(row=0, column=2)
Entry(F6, width=18, textvariable=cosmetic_tax, font="arial 10 bold",
      bd=7, bg="white", fg="black").grid(row=0, column=3)

Label(F6, text="Total Grocery", bg="#a8c8e8", fg="black",
      font=("times new roman", 14, "bold")).grid(row=1, column=0)
Entry(F6, width=18, textvariable=grocery_price, font="arial 10 bold",
      bd=7, bg="white", fg="black").grid(row=1, column=1)

Label(F6, text="Grocery Tax", bg="#a8c8e8", fg="black",
      font=("times new roman", 14, "bold")).grid(row=1, column=2)
Entry(F6, width=18, textvariable=grocery_tax, font="arial 10 bold",
      bd=7, bg="white", fg="black").grid(row=1, column=3)

Label(F6, text="Others Total", bg="#a8c8e8", fg="black",
      font=("times new roman", 14, "bold")).grid(row=2, column=0)
Entry(F6, width=18, textvariable=other_price, font="arial 10 bold",
      bd=7, bg="white", fg="black").grid(row=2, column=1)

Label(F6, text="Others Tax", bg="#a8c8e8", fg="black",
      font=("times new roman", 14, "bold")).grid(row=2, column=2)
Entry(F6, width=18, textvariable=other_tax, font="arial 10 bold",
      bd=7, bg="white", fg="black").grid(row=2, column=3)

# ================= BUTTONS =================

Button(F6, text="Submit", command=total, bg="#1a1a4e", fg="white",
       font=("times new roman", 12, "bold"),
       pady=15, width=10, bd=5).grid(row=0, column=5, padx=10, pady=10)

Button(F6, text="Generate Bill", command=bill_area, bg="#1a1a4e", fg="white",
       font=("times new roman", 12, "bold"),
       pady=15, width=12, bd=5).grid(row=0, column=6, padx=10, pady=10)

btn_save = Button(F6, text="Save Bill", command=save_bill, bg="#1a1a4e", fg="white",
                  font=("times new roman", 12, "bold"),
                  pady=15, width=10, bd=5)
btn_save.grid(row=0, column=7, padx=10, pady=10)
if current_role not in ["admin", "cashier"]:
    btn_save.config(state="disabled", bg="grey", fg="white")

Button(F6, text="Generate PDF", command=generate_pdf, bg="#e67e22", fg="white",
       font=("times new roman", 12, "bold"),
       pady=15, width=10, bd=5).grid(row=0, column=8, padx=10, pady=10)

Button(F6, text="Clear", command=clear_data, bg="#1a1a4e", fg="white",
       font=("times new roman", 12, "bold"),
       pady=15, width=10, bd=5).grid(row=0, column=9, padx=10, pady=10)

Button(F6, text="Search Bills", command=open_search, bg="#27ae60", fg="white",
       font=("times new roman", 12, "bold"),
       pady=15, width=12, bd=5).grid(row=0, column=10, padx=10, pady=10)

Button(F6, text="Dashboard", command=open_streamlit_dashboard,
       bg="#8e44ad", fg="white",
       font=("times new roman", 12, "bold"),
       pady=15, width=10, bd=5).grid(row=0, column=11, padx=10, pady=10)

root.mainloop()