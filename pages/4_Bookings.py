import streamlit as st
import mysql.connector

st.set_page_config(
    page_title="Hotel Management System",
    layout="wide")

def create_connection():
    return mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = st.secrets["mysql_password"],
            database = "hotel_management")

st.title("Booking Management")
st.caption("Manage customer bookings, room assignments and stay details.")
st.header("Create Booking")
connection = create_connection()
cursor = connection.cursor()

cursor.execute( """ SELECT customer_id, first_name, last_name FROM customers ORDER BY first_name """
)

customers = cursor.fetchall()

if customers:
    customer_options = {
        f"{row[1]} {row[2]} (ID: {row[0]})": row[0]
        for row in customers}

    selected_customer = st.selectbox("Select Customer", list(customer_options.keys()))
    selected_customer_id = customer_options[selected_customer]
else:
    st.warning("No customer found. Please register a customer first.")

cursor.close()
connection.close()

connection = create_connection()
cursor = connection.cursor()
cursor.execute(""" SELECT room_id,room_number,room_type,price_per_night 
                FROM rooms WHERE room_status = "Available" ORDER BY room_number """)
available_rooms = cursor.fetchall()
if available_rooms:
    room_options = {f"Room {row[1]}-{row[2]} ({row[3]:.2f}/night)": row[0]
                    for row in available_rooms}
    selected_room = st.selectbox("Select Room", list(room_options.keys()))
    Selected_room_id = room_options[selected_room]
else:
    st.warning("No available rooms found.Please add an available room first.")
cursor.close()
connection.close()

st.subheader("Stay Details")

check_in = st.date_input("Check-In Date",format="DD/MM/YYYY")
check_out = st.date_input("Check-Out Date",format="DD/MM/YYYY")

adults = st.number_input(
    "Number of Adults",
    min_value=1, max_value=10,value = 1, step=1
)

children = st.number_input("Number of Children", min_value=0, max_value=10,
                           value = 0, step=1)

booking_source = st.selectbox("Booking Source",["Walk-in","Website","Phone","Travel Agent","Online Travel Agency"])

if check_out <= check_in:
    st.error("Check-out date must be after check-in date.")
else:
    nights = (check_out-check_in).days
    st.info(f"Number of nights : {nights}")

if check_out > check_in:
    if st.button("Confirm Booking"):
        try:
            connection = create_connection()
            cursor = connection.cursor()
            sql = """ INSERT INTO bookings(customer_id,room_id,booking_date,check_in,check_out,adults,
            children,booking_source,booking_status) VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s) """
            values = (selected_customer_id,Selected_room_id,
                      __import__("datetime").date.today(),check_in,check_out,adults,
                      children,booking_source,"Confirmed")
            cursor.execute(sql,values)
            connection.commit()
            update_room_sql = """ UPDATE rooms SET room_status = "Occupied" WHERE room_id = %s"""
            cursor.execute(update_room_sql,(Selected_room_id,))
            connection.commit()
            st.success("Booking confirmed successfully")
            cursor.close()
            connection.close()
        except mysql.connector.Error as e:
            st.error(f"Database error: {e}")




    