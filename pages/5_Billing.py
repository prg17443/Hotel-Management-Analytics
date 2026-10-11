import streamlit as st
import mysql.connector

st.set_page_config(
    page_title="Hotel Management System",
    layout="wide"
)
def create_connection():
    return mysql.connector.connect(
        host = "localhost",
        user= "root",
        password= st.secrets["mysql_password"],
        database = "hotel_management"
    )
st.title("Billing Management")
st.caption("Manage hotel bills, room charges, additional expenses"
           "taxes, discounts, and payments.")
st.divider()
st.header("Generate New Bill")

connection = create_connection()
cursor = connection.cursor()
cursor.execute(""" SELECT b.booking_id,c.first_name,c.last_name,r.room_number,r.room_type,r.price_per_night,b.check_in,
                    b.check_out,b.booking_status 
                    FROM bookings b JOIN customers c 
                    ON b.customer_id = c.customer_id 
                    JOIN rooms r ON b.room_id = r.room_id WHERE b.booking status IN ('Confirmed','Checked-in','Checked-out')
                    ORDER BY b.booking_id DESC """)
bookings = cursor.fetchall()
cursor.close()
connection.close()
if bookings:
    booking_options = {
        f"Booking {row[0]}-{row[1]}{row[2]} | " f"Room {row[3]} ({row[4]})" : row[0]
        for row in bookings}
    selected_booking = st.selectbox("Select Booking",list(booking_options.keys()))
    selected_booking_id = booking_options[selected_booking]
else:
    st.warning("No eligible bookings found to generate a bill.")