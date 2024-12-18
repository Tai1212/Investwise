import streamlit as st
from backend_api import perform_login, perform_registration, update_or_insert_stock, display_current_stocks
import logging

def main():
    logging.info("starting website user interface")
    st.title("Investwise")
    initialize_session_state()
    if st.session_state.user_authenticated:
        home_section(st.session_state.email)
    else:
        section = st.sidebar.radio("Navigation", ["Login", "Registration"])
        if section == "Login":
            login_section()
        elif section == "Registration":
            registration_section()

def initialize_session_state():
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'email' not in st.session_state:
        st.session_state.username = ""

def login_section():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            login_successful = perform_login({"email": email, "password": password})
            if login_successful:
                st.session_state.user_authenticated = True
                st.session_state.email = email
                st.success(f"{st.session_state.email} successfully logged in!")
                st.rerun()
            else:
                st.warning("Login failed.")
        except Exception as e:
            st.error(str(e))

def registration_section():
    st.subheader("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        try:
            result = perform_registration({"email": email, "password": password})
            if result:
                st.info("Registration successful! Please log in.")
            else:
                st.error("Registration failed. Please try again.")
        except Exception as e:
            st.error(str(e))
    if st.session_state.user_authenticated:
        st.rerun()

def home_section(email):
    st.title("Home Page")
    section = st.sidebar.radio("Navigation", ["Update Stocks", "View Monitored Stocks"])
    if section == "Update Stocks":
        update_stock_section(email)
    elif section == "View Monitored Stocks":
        get_monitored_stocks_section(email)

def update_stock_section(email):
    st.subheader("Update or Insert Stock Information")
    stock_symbol = st.text_input("Stock Symbol")
    purchase_price = st.number_input("Purchase Price")
    target_percentage_change_up = st.number_input("Target Percentage Change Up")
    target_percentage_change_down = st.number_input("Target Percentage Change Down")
    if st.button("Update or Insert Stock"):
        result = update_or_insert_stock({"email": email, "stock_info":{
            "stock_symbol": stock_symbol,
            "purchase_price": purchase_price,
            "last_monitored_percentage_change": 0,
            "target_percentage_change_up": target_percentage_change_up,
            "target_percentage_change_down": target_percentage_change_down
        }})
        st.write(result)

def get_monitored_stocks_section(email):
    st.subheader("Monitored Stocks")
    st.title("Your Monitored Stocks")
    try:
        stocks_dict = display_current_stocks({"email": email})
    except Exception as e:
        st.write(e)
    for stock_symbol, stock_info_list in stocks_dict.items():
        st.header(stock_symbol)
        for stock_info in stock_info_list:
            st.write(stock_info)
