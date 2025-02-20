import streamlit as st
import tabula
import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.DEBUG)

# create a connection to the MySQL database
def create_connection():
    try:
        conn = mysql.connector.connect(
            host='st-python-db.ctwkcywuyqju.us-east-1.rds.amazonaws.com',
            user='admin',
            password='TOP2020%',
            database='python_db'
        )
        if conn.is_connected():
            #logging.debug("Connected to the database")
            return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        #logging.error(f"Error connecting to database: {e}")
    return None

# Create the table if it doesn't exist
def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Customer_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        firstName VARCHAR(255),
        lastName VARCHAR(255),
        email VARCHAR(255) NOT NULL UNIQUE,
        phone VARCHAR(20),
        age INT,
        message TEXT
    );
    """
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
        except Error as e:
            st.error(f"Error creating table: {e}")
            #logging.error(f"Error creating table: {e}")
        finally:
            cursor.close()
            conn.close()

# Function to extract table data from PDF
def extract_data_from_pdf(pdf_file):
    tables = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
    if tables:
        return tables[0].to_dict(orient='records')
    return []

# Function to insert or update data into the database based on email
def insert_or_update_data(data):
    required_fields = ["Email", "First Name", "Last Name", "Phone", "Age", "Message"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    if not missing_fields:
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                insert_query = """
                INSERT INTO Customer_data (email, firstName, lastName, phone, age, message)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    firstName = VALUES(firstName),
                    lastName = VALUES(lastName),
                    phone = VALUES(phone),
                    age = VALUES(age),
                    message = VALUES(message)
                """
                values = (
                    data.get("Email"),
                    data.get("First Name"),
                    data.get("Last Name"),
                    data.get("Phone"),
                    data.get("Age"),
                    data.get("Message")
                )
                cursor.execute(insert_query, values)
                conn.commit()
                return True
            except Error as e:
                st.error(f"Error inserting or updating data for Email: {data.get('Email', 'N/A')}.")
                #logging.error(f"Error inserting or updating data: {e}")
                return False
            finally:
                cursor.close()
                conn.close()
    else:
        st.warning(f"Record for Email: {data.get('Email', 'N/A')} skipped due to missing fields.")
        #logging.warning(f"Missing fields for record: {data}")
        return False

# Streamlit app
def main():
    st.title("PDF Data Inserter")
    create_table()  # Ensure the table exists

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        st.info("PDF uploaded successfully!")
        with st.spinner("Extracting data..."):
            extracted_data = extract_data_from_pdf(uploaded_file)

        if extracted_data:
            st.success("Data extracted successfully!")
            df = pd.DataFrame(extracted_data)
            #st.table(df)

            if st.button("Insert or Update Data into Database"):
                success_count = 0
                failure_count = 0
                for record in extracted_data:
                    if insert_or_update_data(record):
                        success_count += 1
                    else:
                        failure_count += 1
                st.success(f"Number of records inserted or updated: {success_count}")
                st.error(f"Number of records failed: {failure_count}")
        else:
            st.warning("No data found in the PDF. Please check the file structure.")

    st.subheader("Database Records")
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Customer_data")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        if rows:
            columns = ["ID", "First Name", "Last Name", "Email", "Phone", "Age", "Message"]
            data = pd.DataFrame(rows, columns=columns)

            df_with_index = data.set_index("ID")
            styled_data = df_with_index.style.highlight_null(color='yellow')

            st.dataframe(styled_data, width = 1000, height=300 )  # Display the styled table
        else:
            st.info("No records found in the database.")

if __name__ == "__main__":
    main()