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
                    JOIN rooms r ON b.room_id = r.room_id WHERE b.booking_status IN ("Confirmed" , "Checked-in", "Checked-out")
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
    selected_booking_details = next(row for row in bookings
                                    if row[0] == selected_booking_id)
    price_per_night = float(selected_booking_details[5])
    check_in = selected_booking_details[6]
    check_out = selected_booking_details[7]
    nights = (check_out-check_in).days
    rooms_charges = price_per_night*nights
    st.divider()
    st.subheader("Booking Details")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.metric("Rooms Number",selected_booking_details[3])
    with col2:
        st.metric("Nights",nights)
    with col3:
        st.metric("Price per Night",f"Rs{price_per_night:,.2f}")
        st.metric("Total Room Charges",f"Rs{rooms_charges:,.2f}")
    st.divider()
    st.subheader("Additional Charges")
    col1,col2 = st.columns(2)
    with col1:
        food_charges = st.number_input("Food Charges(Rs)",min_value=0.0,value=0.0,step=100.0,key="food_charges")
        services_charges = st.number_input("Services Charges(Rs)",min_value=0.0,value=0.0,step=100.0,key="services_charges")
    with col2:
        discount = st.number_input("Discount(Rs)",min_value=0.0,value=0.0,step=100.0,key="discount")
        tax_rate = st.number_input("Tax Rate(%)",min_value=0.0,value=0.0,max_value=100.0,step=1.0,key="tax_rate")
    st.divider()
    st.subheader("Bill Summary")
    subtotal = (rooms_charges + food_charges + services_charges) #Calculate total charges before discount
    taxable_amount = max(0,subtotal-discount) # calculate amount after discount
    tax_amount = round(taxable_amount * tax_rate/100,2)  #Calculate tax amount
    total_amount = round(taxable_amount + tax_amount,2)   # Calculate final bill amount
    col1,col2 = st.columns(2)   #Display bill calculations
    with col1 :
        st.metric("Rooms Charges",f"Rs{rooms_charges:,.2f}")
        st.metric("Food Charges",f"Rs{food_charges:,.2f}")
        st.metric("Service Charges",f"Rs{services_charges:,.2f}")
    with col2:
        st.metric("Subtotal",f"Rs{subtotal:,.2f}")
        st.metric("Discount",f"Rs{discount:,.2f}")
        st.metric("Tax Amount",f"Rs{tax_amount:,.2f}")
    st.success(f"Final Bill Amount: Rs{total_amount:,.2f}")
    st.divider()
    if st.button("Generate Bill"):
        if discount > subtotal:
            st.error("Discount cannot exceed the subtotal.")
        else:
            connection = None
            cursor = None
            try:
                connection = create_connection()
                cursor = connection.cursor()
                check_sql = """ SELECT bill_id FROM bills WHERE booking_id = %s """
                cursor.execute(check_sql,(selected_booking_id,))
                existing_bill = cursor.fetchone()
                if existing_bill:
                    st.warning(f"A bill already exists for this booking"
                               f"Bill ID:{existing_bill[0]}")
                else:
                    insert_sql = """ INSERT INTO bills (booking_id,rooms_charges,food_charges,services_charges,discount,
                    tax,total_amount,payment_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) """
                    values = (selected_booking_id,rooms_charges,food_charges,services_charges,discount,
                              tax_amount,total_amount,"Pending")
                    cursor.execute(insert_sql,values)
                    connection.commit()
                    st.success(f"Bill generated successfully!!!"
                               f"Bill ID: {cursor.lastrowid}")
            except mysql.connector.Error as e:
                st.error(f"Database error:{e}")
            finally:
                if cursor is not None:
                    cursor.close()
                if connection is not None and connection.is_connected():
                    connection.close()
    st.divider()
    st.header("Billing Records")
    if st.button("View All Bills"):
        connection = None
        cursor = None
        try:
            connection = create_connection()
            cursor = connection.cursor()
            sql = """ SELECT b.bill_id,b.booking_id,c.first_name,c.last_name,r.room_number,b.rooms_charges,b.food_charges,
             b.services_charges,b.discount,b.tax,b.total_amount,b.payment_status FROM bills b JOIN bookings bk
            ON b.booking_id = bk.booking_id JOIN customers c ON bk.customer_id = c.customer_id 
            JOIN rooms r ON bk.room_id = r.room_id ORDER BY b.bill_id DESC """
            cursor.execute(sql)
            bills = cursor.fetchall()
            if bills:
                columns = ["Bill ID","Booking ID","First Name","Last Name","Room Number","Room Charges","Food Charges",
                           "Services Charges","Discount","Tax","Total Amount","Payment Status"]
                bill_records = [dict(zip(columns,row)) for row in bills]
                st.dataframe(bill_records,use_container_width=True)
            else:
                st.info("No billing records found.")
        except mysql.connector.Error as e:
            st.error(f"Database error:{e}")
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()
    st.divider()
    st.header("Update Payment Status")
    connection = None
    cursor = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(""" SELECT bill_id,booking_id,total_amount,payment_status FROM bills ORDER BY bill_id DESC """)
        payment_records = cursor.fetchall()
        if payment_records:
            bill_options = {f"Bill {row[0]} | Booking {row[1]} |"
                            f"Rs{float(row[2]):,.2f}| {row[3]}": row[0] for row in payment_records}
            selected_bill = st.selectbox("Select Bill",list(bill_options.keys()),
                                         key="payment_bill")
            selected_bill_id = bill_options[selected_bill]
            new_payment_status = st.selectbox("Select Payment Status",["Pending","Paid"], key="new_payment_status")
            if st.button("Update Payment Status"):
                update_sql = """ UPDATE bills SET payment_status = %s WHERE bill_id = %s """
                cursor.execute(update_sql,(new_payment_status,selected_bill_id))
                connection.commit()
                st.success(f"Bill {selected_bill_id} payment status"
                           f"Updated to {new_payment_status}!")
        else:
            st.info("No bills available to update.")
    except mysql.connector.Error as e:
        st.error(f"Database error : {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
    st.divider()
    st.header("Search Bill")
    search_bill_id = st.number_input("Enter Bill Id",min_value=1,step=1,key="search_bill_id")
    if st.button("Search Bill"):
        connection = None
        cursor = None
        try:
            connection = create_connection()
            cursor = connection.cursor()
            sql = """ SELECT b.bill_id,b.booking_id,c.first_name,c.last_name,r.room_number,b.rooms_charges,b.food_charges,
            b.services_charges,b.discount,b.tax,b.total_amount,b.payment_status FROM bills b JOIN bookings bk ON b.booking_id = 
            bk.booking_id JOIN customers c ON bk.customer_id = c.customer_id JOIN rooms r ON bk.room_id = r.room_id WHERE 
             b.bill_id = %s """
            cursor.execute(sql,(search_bill_id,))
            bill = cursor.fetchone()
            if bill :
                columns = ["Bill ID","Booking ID","First Name","Last Name","Room Number","Rooms charges","Food charges",
                           "Services Charges","Discount","Tax","Total Amount","Payment Status"]
                bill_records = dict(zip(columns,bill))
                st.dataframe([bill_records],use_container_width=True)
            else:
                st.warning("No bill found with that ID.")
        except mysql.connector.Error as e :
            st.error(f"Database error: {e}")
        finally :
            if cursor is not None :
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()
else:
    st.warning("No eligible bookings found to generate a bill.")

