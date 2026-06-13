import streamlit as st
import mysql.connector
import pandas as pd

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# ================= THEME (LIGHT BLUE + CLEAN UI) =================
st.markdown("""
    <style>

        /* VERY LIGHT BLUE BACKGROUND */
        .stApp {
            background-color: #e3efff;
        }

        /* HEADINGS */
        h1, h2, h3 {
            color: #000 !important;
            font-weight: 800;
        }

        /* KPI BOXES */
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #d6e2f0;
        }

        div[data-testid="metric-container"] * {
            color: #000 !important;
            font-weight: 700;
        }

        /* DATAFRAME CONTAINER */
        div[data-testid="stDataFrame"] {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #d6e2f0;
        }

        /* TABLE HEADER */
        thead tr th {
            background-color: #f3f6fb !important;
            color: #000 !important;
            font-weight: 800 !important;
            text-align: left !important;
        }

        /* TABLE CELLS */
        tbody tr td {
            color: #000 !important;
            font-weight: 500 !important;
            text-align: left !important;
        }

    </style>
""", unsafe_allow_html=True)

# ================= DATABASE CONNECTION =================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="billingdb1"
)
cursor = conn.cursor()

# ================= TITLE =================
st.title("📊 Retail Store Analytics Dashboard")

# ================= FETCH DATA =================
cursor.execute("SELECT COUNT(*), IFNULL(SUM(grand_total),0) FROM flexible_bills")
total_bills, total_sales = cursor.fetchone()

cursor.execute("SELECT IFNULL(SUM(tax_cosmetics + tax_grocery + tax_others),0) FROM flexible_bills")
total_tax = cursor.fetchone()[0]

net_revenue = total_sales - total_tax

cursor.execute("""
    SELECT IFNULL(SUM(total_cosmetics),0),
           IFNULL(SUM(total_grocery),0),
           IFNULL(SUM(total_others),0)
    FROM flexible_bills
""")
cos, gro, oth = cursor.fetchone()

cursor.execute("""
    SELECT customer_name, SUM(grand_total)
    FROM flexible_bills
    GROUP BY customer_name
    ORDER BY SUM(grand_total) DESC
    LIMIT 5
""")
top_customers = cursor.fetchall()

cursor.execute("""
    SELECT bill_no, customer_name, phone_no, grand_total
    FROM flexible_bills
    ORDER BY bill_no DESC
    LIMIT 10
""")
recent_bills = cursor.fetchall()

# ================= KPI SECTION =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Bills", total_bills)
col2.metric("Total Sales", f"₹ {total_sales:.0f}")
col3.metric("Total Tax", f"₹ {total_tax:.0f}")
col4.metric("Net Revenue", f"₹ {net_revenue:.0f}")

st.divider()

# ================= CATEGORY CHART =================
st.subheader("📦 Category-wise Sales")

df_cat = pd.DataFrame({
    "Category": ["Cosmetics", "Grocery", "Others"],
    "Sales": [cos, gro, oth]
})

st.bar_chart(df_cat.set_index("Category"), use_container_width=True)

st.divider()

# ================= TOP CUSTOMERS =================
st.subheader("🏆 Top Customers")

df_customers = pd.DataFrame(top_customers, columns=["Customer", "Total Amount"])
df_customers["Total Amount"] = df_customers["Total Amount"].apply(lambda x: f"₹ {x:.0f}")

st.dataframe(df_customers, use_container_width=True, height=250)

st.divider()

# ================= RECENT BILLS =================
st.subheader("🧾 Recent Bills")

df_bills = pd.DataFrame(
    recent_bills,
    columns=["Bill No", "Customer", "Phone", "Grand Total"]
)

df_bills["Grand Total"] = df_bills["Grand Total"].apply(lambda x: f"₹ {x:.0f}")

st.dataframe(df_bills, use_container_width=True, height=300)

# ================= FOOTER =================
st.caption("Retail Billing System • Streamlit + MySQL • Light Blue Professional Dashboard")


# import streamlit as st
# import mysql.connector
# import pandas as pd

# # ================= PAGE CONFIG =================
# st.set_page_config(page_title="Retail Dashboard", layout="wide")

# # ================= BACKGROUND =================
# st.markdown("""
#     <style>
#         .stApp {
#             background-color: #b6d1ec;
#         }

#         h1, h2, h3 {
#             color: #000 !important;
#             font-weight: 800;
#         }

#         .block-container {
#             padding-top: 2rem;
#         }

#         /* KPI BOX */
#         div[data-testid="metric-container"] {
#             background-color: #ffffff;
#             border: 1px solid #8aa9c7;
#             border-radius: 12px;
#             padding: 12px;
#         }

#         div[data-testid="metric-container"] label,
#         div[data-testid="metric-container"] div {
#             color: #000 !important;
#             font-weight: 700;
#         }

#         /* CUSTOM TABLE CARD */
#         .table-card {
#             background-color: #ffffff;
#             padding: 15px;
#             border-radius: 12px;
#             box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
#         }

#         table {
#             width: 100%;
#             border-collapse: collapse;
#             font-size: 15px;
#         }

#         th {
#             text-align: left;
#             background-color: #f2f6fb;
#             color: #000;
#             padding: 10px;
#             border-bottom: 2px solid #d0d7e2;
#         }

#         td {
#             padding: 10px;
#             border-bottom: 1px solid #e6e9ef;
#             color: #000;
#             font-weight: 500;
#             text-align: left;
#         }

#         tr:hover {
#             background-color: #eef4ff;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # ================= DB =================
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="billingdb1"
# )
# cursor = conn.cursor()

# # ================= TITLE =================
# st.title("📊 Retail Store Analytics Dashboard")

# # ================= DATA =================
# cursor.execute("""
#     SELECT COUNT(*), IFNULL(SUM(grand_total),0)
#     FROM flexible_bills
# """)
# total_bills, total_sales = cursor.fetchone()

# cursor.execute("""
#     SELECT IFNULL(SUM(tax_cosmetics + tax_grocery + tax_others),0)
#     FROM flexible_bills
# """)
# total_tax = cursor.fetchone()[0]

# net_revenue = total_sales - total_tax

# cursor.execute("""
#     SELECT 
#         IFNULL(SUM(total_cosmetics),0),
#         IFNULL(SUM(total_grocery),0),
#         IFNULL(SUM(total_others),0)
#     FROM flexible_bills
# """)
# cos, gro, oth = cursor.fetchone()

# cursor.execute("""
#     SELECT customer_name, SUM(grand_total)
#     FROM flexible_bills
#     GROUP BY customer_name
#     ORDER BY SUM(grand_total) DESC
#     LIMIT 5
# """)
# top_customers = cursor.fetchall()

# cursor.execute("""
#     SELECT bill_no, customer_name, phone_no, grand_total
#     FROM flexible_bills
#     ORDER BY bill_no DESC
#     LIMIT 10
# """)
# recent_bills = cursor.fetchall()

# # ================= KPI =================
# col1, col2, col3, col4 = st.columns(4)

# col1.metric("Total Bills", total_bills)
# col2.metric("Total Sales", f"₹ {total_sales:.0f}")
# col3.metric("Total Tax", f"₹ {total_tax:.0f}")
# col4.metric("Net Revenue", f"₹ {net_revenue:.0f}")

# st.divider()

# # ================= CATEGORY =================
# st.subheader("📦 Category-wise Sales")

# df_cat = pd.DataFrame({
#     "Category": ["Cosmetics", "Grocery", "Others"],
#     "Sales": [cos, gro, oth]
# })

# st.bar_chart(df_cat.set_index("Category"), use_container_width=True)

# st.divider()

# # ================= TABLE RENDER FUNCTION =================
# def render_table(df):
#     return f"""
#     <div class="table-card">
#         {df.to_html(index=False, escape=False)}
#     </div>
#     """

# # ================= TOP CUSTOMERS =================
# st.subheader("🏆 Top Customers")

# df_customers = pd.DataFrame(top_customers, columns=["Customer", "Total Amount"])
# df_customers["Total Amount"] = df_customers["Total Amount"].apply(lambda x: f"₹ {x:.0f}")

# st.markdown(render_table(df_customers), unsafe_allow_html=True)

# st.divider()

# # ================= RECENT BILLS =================
# st.subheader("🧾 Recent Bills")

# df_bills = pd.DataFrame(
#     recent_bills,
#     columns=["Bill No", "Customer", "Phone", "Grand Total"]
# )

# df_bills["Grand Total"] = df_bills["Grand Total"].apply(lambda x: f"₹ {x:.0f}")

# st.markdown(render_table(df_bills), unsafe_allow_html=True)

# # ================= FOOTER =================
# st.caption("Retail Billing System • Streamlit + MySQL • Styled White Tables Dashboard")


