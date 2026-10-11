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

            check_sql = """ SELECT booking_id FROM bookings WHERE room_id = %s AND booking_status IN ("Confirmed","Checked-in") 
             AND check_in < %s AND check_out > %s """
            
            check_values = (Selected_room_id,check_out,check_in)

            cursor.execute(check_sql,check_values)
            existing_booking = cursor.fetchone()
            if existing_booking:
                st.error(f"This room is already booked during the selected dates,"
                         f"Existing Booking ID: {existing_booking[0]}")
            else:
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
st.divider()
st.header("Booking Management")
if st.button("View All Bookings"):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(""" SELECT b.booking_id,c.first_name,c.last_name,r.room_number,r.room_type,b.booking_date,
        b.check_in,b.check_out,b.adults,b.children,b.booking_source,b.booking_status FROM bookings b JOIN customers c ON
        b.customer_id = c.customer_id JOIN rooms r ON b.room_id = r.room_id ORDER BY b.booking_id """)

        bookings = cursor.fetchall()
        cursor.close()
        connection.close()

        if bookings:
            columns = ["Booking ID","First Name","Last Name","Room Number","Room type","Booking date","Check-In Date",
                       "Check-Out Date","Adults","Children","Booking Source","Booking Status"]
            st.dataframe([dict(zip(columns,row)) for row in bookings], use_container_width= True)
        else:
            st.info("No bookings found.")
    except mysql.connector.Error as e:
        st.error(f"Database error:{e}")

st.divider()
st.header("Search Booking")
search_booking_id = st.number_input("Enter Booking ID", min_value=1,step=1)
if st.button("Search Booking"):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT b.booking_id,c.first_name,c.last_name,r.room_number,r.room_type,b.booking_date,
        b.check_in,b.check_out,b.adults,b.children,b.booking_source,b.booking_status FROM bookings b JOIN customers c ON
        b.customer_id = c.customer_id JOIN rooms r ON b.room_id = r.room_id  WHERE b.booking_id = %s """,(search_booking_id,))

        booking = cursor.fetchone()
        cursor.close()
        connection.close()

        if booking:
            columns = ["Booking ID","First Name","Last Name","Room Number","Room type","Booking date","Check-In Date",
                       "Check-Out Date","Adults","Children","Booking Source","Booking Status"]
            st.dataframe([dict(zip(columns,booking))], use_container_width=True)
        else:
            st.warning("No Booking found wih this ID.")

    except mysql.connector.Error as e:
        st.error(f"Database error : {e}")
st.divider()
st.subheader("Update Booking Status")

update_booking_id = st.number_input("Enter Booking ID to Update",min_value=1,step=1,key="update_booking_id")
new_bookings_status = st.selectbox("Select New Booking Status",["Confirmed","Checked-in","Checked-out","Cancelled"],
                                   key="new_booking_status")
if st.button("Update Bookings Status"):
    try:
        connection=create_connection()
        cursor = connection.cursor()
        cursor.execute(""" SELECT booking_status FROM bookings WHERE booking_id = %s """,(update_booking_id,))
        booking = cursor.fetchone()
        if booking is None:
            st.warning("No booking found with this ID.")
        else:
            cursor.execute(""" UPDATE bookings SET booking_status = %s WHERE booking_id = %s""",
                           (new_bookings_status,update_booking_id))
            connection.commit()
            st.success(f"Booking ID{update_booking_id} status" f"Updated to {new_bookings_status}!")
            cursor.close()
            connection.close()
    except mysql.connector.Error as e:
        st.error(f"Database error : {e}")

st.divider()
st.header("Edit Booking Details")

edit_booking_id = st.number_input("Enter Booking ID to Edit", min_value=1, step= 1, key="edit_booking Details")
if st.button("Load Booking Details"):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = """ SELECT booking_id,customer_id,room_id,check_in,check_out,adults,children,booking_source,
        booking_status FROM bookings WHERE booking_id = %s """

        cursor.execute(sql,(edit_booking_id,))
        booking = cursor.fetchone()
        cursor.close()
        connection.close()

        if booking:
            st.session_state["edit_booking"] = booking
            if booking[8] == "Cancelled":
                st.warning("This booking has been cancelled."
                           "Its details can be viewed, but it cannot be edited.")
            else:
                st.success("Booking details loaded successfully!!!")
        else: 
            st.session_state.pop("edit _booking",None)
            st.warning("Booking Not found")

    except mysql.connector.Error as e:
        st.error(f"Database error:{e}")

booking = st.session_state.get("edit_booking")

if booking and booking[8] != "Cancelled":
    st.subheader("Edit Booking Information")
    st.write(f"Booking ID : {booking[0]}")
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(""" SELECT room_id,room_number,room_type,price_per_night FROM rooms ORDER BY room_number """)
    rooms = cursor.fetchall()
    cursor.close()
    connection.close()
    if rooms:
        room_options = {f"Room{row[1]}-{row[2]}(Rs{row[3]:.2f}/night)": row[0]
                        for row in rooms}
        room_labels = list(room_options.keys())
        current_room_index = next( (i for i, row in enumerate(rooms)
                                  if row[0] == booking[2]),0)
        room_edit = st.selectbox("Select Room",room_labels,index=current_room_index,key="room_edit")
        selected_room_edit_id = room_options[room_edit]
    else:
        st.warning("No rooms found.")

    adults_edit = st.number_input("Number of Adults",min_value=1,max_value=10,value= int(booking[5]),step=1,key="adults edit")
    children_edit = st.number_input("Number of Children",min_value=0,max_value=10,value=int(booking[6]),step=1,key="children_edit")
    booking_source_options = ["Walk-in","Website","Phone","Travel Agent","Online Travel Agency"]
    booking_source_edit = st.selectbox("Booking Source",booking_source_options,index=booking_source_options.index(booking[7]),
                                       key="booking_source_edit")
    st.subheader("Edit Stay Dates")

    check_in_edit = st.date_input("Check-in Date",value=booking[3],format="DD/MM/YYYY",key="check_in_edit")
    check_out_edit = st.date_input("Check-out Date",value=booking[4],format="DD/MM/YYYY",key="check_out_edit")

    st.divider()
    if st.button("Update Booking",key="update_booking"):
        if check_out_edit <= check_in_edit:
            st.error("Check-out date must be after check-in date.")
        else:
            try:
                connection = create_connection()
                cursor = connection.cursor()
                check_sql = """ SELECT booking_id FROM bookings WHERE room_id = %s AND booking_status IN ('Confirmed','Checked-in')
                AND check_in < %s AND check_out > %s AND booking_id != %s """

                check_values = (selected_room_edit_id,check_out_edit,check_in_edit,booking[0])
                cursor.execute(check_sql,check_values)
                existing_booking = cursor.fetchone()

                if existing_booking:
                    st.error("This room is already booked during the selected dates"
                             f"Conflicting Booking ID : {existing_booking[0]}")
                else:
                    update_sql = """ UPDATE bookings SET room_id = %s, check_in = %s, check_out = %s, adults = %s, children = %s,
                    booking_source = %s WHERE booking_id = %s """
                    update_values = (selected_room_edit_id,check_in_edit,check_out_edit,adults_edit,children_edit,booking_source_edit,
                                    booking[0])
                    cursor.execute(update_sql,update_values)
                    connection.commit()
                    st.success("Booking Updated Successfully!")
                    updated_booking = list(booking)
                    updated_booking[2] = selected_room_edit_id
                    updated_booking[3] = check_in_edit
                    updated_booking[4] = check_out_edit
                    updated_booking[5] = adults_edit
                    updated_booking[6] = children_edit
                    updated_booking[7] = booking_source_edit
                    st.session_state["edit_booking"] = tuple(updated_booking)
            except mysql.connector.Error as e:
                st.error(f"Database error: {e}")
            finally:
                if cursor is not None:
                    cursor.close()
                    if connection is not None and connection.is_connected():
                        connection.close()