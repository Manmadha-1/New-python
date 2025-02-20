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


