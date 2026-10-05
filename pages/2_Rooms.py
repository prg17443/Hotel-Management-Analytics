import streamlit as st
import mysql.connector

st.set_page_config(
    page_title= "Hotel Management System",
    layout="wide"
)

def create_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = st.secrets["mysql_password"],
        database = "hotel_management"
    )

st.title("Hotel Management System")
st.caption("Manage hotel rooms, room types, pricing and availability.")

st.header("Room Registration")

with st.form("room_registration_form"):
    room_number = st.text_input("Room Number")
    room_type = st.selectbox("Room Type",["Select","Standard","Deluxe","Suite"])
    price_per_night = st.number_input("Price per night",min_value=0.0,step=100.0)
    capacity = st.number_input("Capacity",min_value=1,max_value=10,step=1)
    submit_room = st.form_submit_button("Add Room")

if submit_room:
    if room_number.strip() == "":
        st.error("Please enter room number.")
    elif room_type == "Select":
        st.error("Please select room type.")
    elif price_per_night <= 0:
        st.error("Please enter a valid room price.")
    else:
        try:
            connection = create_connection()
            cursor = connection.cursor()
            sql = """ Insert INTO rooms (room_number,room_type,price_per_night,capacity) VALUES (%s,%s,%s,%s) """
            values = (room_number.strip(),room_type,price_per_night,capacity)

            cursor.execute(sql,values)
            connection.commit()
            st.success("Room added successfully!")
            cursor.close()
            connection.close()
        except mysql.connector.Error as e:
            st.error(f"Database error:{e}")

st.divider()
st.header("Room Management")

if st.button("View All Rooms"):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(""" SELECT room_id,room_number,room_type,price_per_night,capacity,room_status FROM rooms ORDER BY room_id """)
        rooms = cursor.fetchall()
        cursor.close()
        connection.close()

        if rooms:
            st.dataframe(rooms, use_container_width=True)
        else:
            st.info("No rooms found.")

    except mysql.connector.Error as e :
        st.error(f"Database error:{e}")

st.subheader("Search Room")
search_room = st.text_input("Enter Room Number", placeholder="Example : 101")
if st.button("Search Room"):
    if search_room.strip() == "":
        st.warning("Please enter a room number.")
    else:
        try:
            connection = create_connection()
            cursor= connection.cursor()
            search_sql = """ SELECT room_id,room_number,room_type,price_per_night,capacity,room_status FROM rooms 
            WHERE room_number = %s """
            cursor.execute(search_sql,(search_room.strip(),))
            room = cursor.fetchone()
            cursor.close()
            connection.close()

            if room:
                st.dataframe([room], use_container_width= True)
            else:
                st.info("No room found.")
        except mysql.connector.Error as e:
            st.error(f"Database error:{e}")

st.subheader("Update Room")
room_id = st.number_input("Enter Room ID", min_value=1, step=1)
if st.button("Load Room"):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(""" SELECT room_id,room_number,room_type,price_per_night,capacity,room_status FROM rooms 
        WHERE room_id = %s """, (room_id,))

        room = cursor.fetchone()
        cursor.close()
        connection.close()

        if room:
            st.session_state["room"] = room
            st.success("Room loaded sucessfully!")
        else:
            st.warning("Room not found")
    except mysql.connector.Error as e:
        st.error(f"Database error:{e}")

room = st.session_state.get("room")
if room :
    st.write("### Edit Room Details")
    room_number_edit = st.text_input("Room Number",value=room[1])
    room_type_options = ["Standard","Deluxe","Suite"]
    room_type_edit = st.selectbox("Room Type",room_type_options, index= room_type_options.index(room[2]))
    price_edit = st.number_input("Price per Night",min_value=0.0,value=float(room[3]),step=100.0)
    capacity_edit = st.number_input("Capacity",min_value=1,max_value=10,value = int(room[4]),step=1)
    room_status_options = ["Available","Occupied","Maintenance"]
    room_status_edit = st.selectbox("Room Status",room_status_options,index= room_status_options.index(room[5]))

if st.button("Update Room"):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = """ UPDATE rooms SET room_number = %s , room_type = %s, price_per_night = %s, capacity = %s,
                  room_status = %s WHERE room_id = %s """
        values = (room_number_edit.strip(), room_type_edit,price_edit,capacity_edit,room_status_edit,room_id)
        cursor.execute(sql,values)
        connection.commit()
        st.success("Room Updated Successfully!!")
        cursor.close()
        connection.close()
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")

if submit_room:
    check_sql = """ SELECT room_id FROM rooms wHERE room_number = %s """
    cursor.execute(check_sql,(room_number.strip(), ))
    existing_room = cursor.fetchone()

if existing_room:
    st.warning("Room number already exists.")
else:
    sql = """ INSERT INTO rooms (room_number,room_type,price_per_night,capacity) VALUES (%s,%s,%s,%s) """
    values = (room_number.strip(),room_type,price_per_night,capacity)

    cursor.execute(sql,values)
    connection.commit()
    st.success("Room Added Successfully!!!")


        