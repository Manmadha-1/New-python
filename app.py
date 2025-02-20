import streamlit as st
import mysql.connector
import pandas as pd
import logging
from mysql.connector import Error

st.title('My first app')
st.write('Here\'s welcome message')
st.write('Here\'s our first attempt at using data to create a table:')

def create_connection():
    try:
        conn = mysql.connector.connect(
            host='database-1.ctwkcywuyqju.us-east-1.rds.amazonaws.com',
            user='admin',
            password='TOP2020%',
            database='database-1'
        )
        if conn.is_connected():
            logging.debug("Connected to the database")
            return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
    return None

def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS account (
        id INT AUTO_INCREMENT primary key,
        firstName VARCHAR(255),
        lastName VARCHAR(255),
        email VARCHAR(255) NOT NULL UNIQUE,
        phone VARCHAR(20),
        age INT,
        message LONGTEXT
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
        finally:
            cursor.close()
            conn.close()

def insert_data(firstName, lastName, email, phone, age, message):
    conn = create_connection()
    if conn:
        try:
            insert_query = """
            INSERT INTO account (firstName, lastName, email, phone, age, message)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor = conn.cursor()
            cursor.execute(insert_query, (firstName, lastName, email, phone, age, message))
            conn.commit()
            return True
        except Error as e:
            st.error(f"Error inserting data: {e}")
        finally:
            cursor.close()
            conn.close()
    return False



