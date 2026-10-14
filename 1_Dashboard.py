import streamlit as st
import mysql.connector
st.set_page_config(
    page_title="Hotel Management Dashboard",
    layout="wide"
)

def create_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = st.secrets["mysql_password"],
        database = "hotel_management"
    )
st.title("Hotel Management Dashboard")
st.caption("Monitor hotel customers,rooms,bookings and billing.")
st.divider()
try:
    connection = create_connection()
    if connection.is_connected():
        st.success("Mysql database connected successfully!!!")
except mysql.connector.Error as error:
    st.error(f"Database Connection failed: {error}")
finally:
    if "connection" in locals() and connection.is_connected():
        connection.close()
st.divider()
st.header("Hotel Overview")
try:
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    st.metric(label="Total Customers",value=total_customers)
except mysql.connector.Error as error:
    st.error(f"Unable to load customer data: {error}")
finally:
    if "cursor" in locals() and cursor:
        cursor.close()
    if "connection" in locals() and connection and connection.is_connected():
        connection.close()
        
