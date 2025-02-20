import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd # for table format
import re

# Function to create the database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='st-python-db.ctwkcywuyqju.us-east-1.rds.amazonaws.com',
            user='admin',
            password='TOP2020%',
            database='python_db'
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Function to create a table if it doesn't exist
def create_table():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstName VARCHAR(100) NOT NULL,
                lastName VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20) NOT NULL,
                age INT NOT NULL,
                message LONGTEXT
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

# Email Validation
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_pattern, email) is not None

# Phone Number Validation
def is_valid_phone(phone):
    phone_pattern = r'^\+?\d{1,4}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    return re.match(phone_pattern, phone) is not None

# Function to insert data into the table
def insert_data(firstName, lastName, email, phone, age, message):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql = 'INSERT INTO Contacts (firstName, lastName, email, phone, age, message) VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (firstName, lastName, email, phone, age, message))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f'Error inserting data: {e}')
            return False
# Initialize the database and table
create_table()

st.markdown("<h1 style='color:#4c81af;'>Contact Information</h1>", unsafe_allow_html=True)


# create a form with iput fields    
with st.form("contact_form"):
    st.markdown("### **Enter Your Details**") 
    firstname = st.text_input('First Name :red[*] (required)')
    lastname = st.text_input('Last Name :red[*] (required)')
    email = st.text_input('Email :red[*] (required)')
    phone = st.text_input('Phone :red[*] (required)')
    age = st.number_input('Age :red[*] (required)', min_value=18, step=1)
    message = st.text_area('Message')
    
    # Submit Button
    submitted = st.form_submit_button("Submit")
    
    if submitted:

        if not firstname:
            st.error('Please enter your first name')        
            st.stop()

        if not lastname:
            st.error('Please enter your Last name')        
            st.stop()

        if not email:
            st.error('Please enter your Email')        
            st.stop()
        
        if not is_valid_email(email):
            st.error('Please enter Valid Email Address')        
            st.stop()

        if not phone :
            st.error('Please enter your Phone Number')        
            st.stop()

        if not is_valid_phone(phone):
            st.error('Please enter Valid Phone Number')        
            st.stop()

        if not age :
            st.error('Please enter your Age')        
            st.stop()
            
        success = insert_data(firstname, lastname, email, phone, int(age), message )
        if success:
            st.success('Data inserted successfully')
        else:
            st.error('Failed to insert data.')

# Display all data from the table
st.subheader("Database Records")
connection = create_connection()
if connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Contacts")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    if rows:
        columns = ["ID", "First Name", "Last Name", "Email", "Phone", "Age", "Message"]
        df = pd.DataFrame(rows, columns=columns)
        df_with_index = df.set_index("ID")
        st.write(df_with_index)
    else:
        st.info("No records found in the database.")
