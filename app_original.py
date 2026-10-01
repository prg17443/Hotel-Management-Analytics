import streamlit as st
import mysql.connector
from pathlib import Path
import base64

def create_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = st.secrets["mysql_password"],
        database = "hotel_management"
    )

st.set_page_config(
    page_title="Hotel Management System",
    page_icon="HOTEL_LOGO.jpeg",
    layout="wide"
)

logo_path = Path(__file__).parent / "HOTEL_LOGO.jpeg"
left,center,right = st.columns([1,2,1])
with center:
    st.markdown(
    """ 
    <h1 style = "
            text-align:center
            font-size: 36px;
            font-weight: 700;
            margin-top: 10px ;
            margin-bottom: 15px;
            white-space: nowrap;
        ">
            HOTEL MANAGEMENT SYSTEM
        </h1>
        """,
        unsafe_allow_html=True)

with open(logo_path,"rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

st.markdown(f""" 
    <div style = "
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0 15px 0">
         <img  
                src = "data:image/jpeg;base64,{logo_base64}"
                width= "110"
                style = "border-radius:10px;">
    </div>
    """, unsafe_allow_html=True)

st.markdown( """ <p style = "
            text-align:center;
            font-size: 18px;
            margin-top: 10px;
            margin-bottom: 20px;
        ">
            Customer Management & Analytics System
        </p>
    """,
    unsafe_allow_html=True
)

st.divider()

st.header("Customer Registration")

with st.form("customer_registration_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    gender = st.selectbox("Gender",["Select","Male","Female","Other"])
    age = st.number_input("Age",min_value=1, max_value=100,step = 1)
    city = st.text_input("City")
    state = st.text_input("State")
    country = st.text_input("Country")
    nationality = st.text_input("Nationality")

    submit = st.form_submit_button("Register Customer") 

if submit:
    if first_name.strip() == "":
        st.error("Please enter first name.")
    elif last_name.strip() == "":
        st.error("Please Enter last name.")
    elif gender == "Select":
        st.error("Please select gender.")
    elif city.strip() == "":
        st.error("Please enter city.")
    elif state.strip() == "":
        st.error("Please Enter state.")
    elif country.strip() == "":
        st.error("Please Enter Country.")
    elif nationality.strip() == "":
        st.error("Please Enter Nationality.")           
    else:
        try:       
            connection = create_connection()
            cursor = connection.cursor()
            check_sql = """ 
            SELECT customer_id FROM customers WHERE first_name = %s AND last_name = %s AND age = %s AND city = %s """

            check_values = (first_name.strip(),
                            last_name.strip(), age , city.strip())
            
            cursor.execute(check_sql,check_values)
            existing_customer = cursor.fetchone()

            if existing_customer:
                st.warning(
                    f"Customer Already Exists With Customer ID: "
                    f"{existing_customer[0]}"
                )
            else:
                sql = """ 
            INSERT INTO customers (first_name, last_name, gender, age, city, state, country,nationality) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) 
            """

            values = (first_name.strip(),
                      last_name.strip(),
                      gender,age,
                      city.strip(),
                      state.strip(),country.strip(),nationality.strip())

            cursor.execute(sql,values)

            connection.commit()
            st.success("Customer Registered Successfully !!!")
            cursor.close()
            connection.close()    
        except mysql.connector.Error as e:
            st.error(f"Database error:{e}")

st.divider()
st.header("Customer Management")
if st.button("View All Customers"):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(""" SELECT customer_id,first_name,last_name,gender,age,city,state,country,nationality,created_at FROM customers
         ORDER BY customer_id """)

        customers = cursor.fetchall()
        cursor.close()
        connection.close()

        if customers:

            st.dataframe( customers,
                         use_container_width=True)
        else:
            st.info("No Customers Found.")
    except mysql.connector.Error as e :
        st.error(f"Database error: {e}")
st.subheader("Search Customer")
search_name = st.text_input("Enter customer name",placeholder="Example: Priya")

if st.button("Search Customer"):

    if search_name.strip() == "":
        st.warning("Please enter a customer name.")
    else:
        try:
            connection= create_connection()
            cursor = connection.cursor()

            search_sql = """ SELECT customer_id,first_name,last_name,gender,age,city,state,country,nationality,
            created_at FROM customers WHERE first_name LIKE %s OR last_name LIKE %s ORDER BY customer_id """

            search_value = "%"+ search_name.strip() +"%"

            cursor.execute(search_sql,(search_value,search_value))

            results = cursor.fetchall()

            cursor.close()
            connection.close()

            if results:
                st.dataframe(results,use_container_width=True)
            else:
                st.info("No customer found.")
            
        except mysql.connector.Error as e :
                st.error(f"Database error : {e}")


