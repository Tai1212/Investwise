import streamlit as st
from backend_api import perform_login, perform_registration, update_or_insert_stock

def main():
    st.title("Investwise")
    initialize_session_state()
    if st.session_state.user_authenticated:
        update_stock_section(st.session_state.email)
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
    email = st.text_input("Email1")
    password = st.text_input("Password1", type="password")
    if st.button("Login"):
        result = perform_login({"email": email, "password": password})
        if result:
            st.session_state.user_authenticated = True
            st.session_state.email = email
            st.success(f"{st.session_state.email} successfully logged in!")
            st.rerun()
        else:
            st.warning("Login failed.")

def registration_section():
    st.subheader("Register")
    email = st.text_input("email")
    password = st.text_input("Password2", type="password")
    if st.button("Register"):
        result = perform_registration({"email": email, "password": password})
        if result:
            st.info("Please log in to the website.")
    if st.session_state.user_authenticated:
        st.rerun()

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
            "target_percentage_change_up": target_percentage_change_up,
            "target_percentage_change_down": target_percentage_change_down
        }})
        st.write(result)

if __name__ == "__main__":
    main()
