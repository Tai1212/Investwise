import streamlit as st
import httpx
import logging

backend_base_url = "http://backend_container:8001"
logging.root.setLevel(logging.INFO)

def make_api_request(url, payload):
    response = httpx.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["Message"]
    else:
        return f"Error: {response.status_code}"

def perform_login(login_request):
    api_url = f"{backend_base_url}/Login"
    try:
        logging.info("perform_login calling httpx.post with api_url={}, json={}".format(api_url, login_request))
        response = httpx.post(api_url, json=login_request, timeout=45)
        response.raise_for_status()
        result = response.json()["Message"]
        if "Login successful!" in result:
            st.success(f"Login successful for {login_request['email']}!")
            return True
        elif "Incorrect password." in result:
            st.warning("Incorrect password, please try again.")
            return False
        else:
            st.warning("User not found.")
            return False
    except httpx.RequestError as e:
        st.error(f"Error during login request: {e}")
        return False
    except httpx.HTTPStatusError as e:
        st.error(f"HTTP error during login request: {e}")
        return False
    
def perform_registration(login_request):
    api_url = f"{backend_base_url}/Register"
    try:
        response = httpx.post(api_url, json=login_request, timeout=30)
        response.raise_for_status()
        result = response.json()['Message']
        print("result: {}".format(result))
        if "User registered successfully!" in result:
            st.success(f"Registration successful for {login_request['email']}!")
            return True
        elif "Username already exists" in result:
            st.warning("Registration failed. Please choose a different username.")
            return False
        else:
            st.warning("Registration failed. Unknow error.")
            return False
    except httpx.RequestError as e:
        st.error(f"Error during registration request: {e}")
        return False
    except httpx.HTTPStatusError as e:
        st.error(f"HTTP error during registration request: {e}")
        return False

def update_or_insert_stock(stock_info_payload):
    api_url = f"{backend_base_url}/update_or_insert_stock"
    try:
        response = httpx.post(api_url, json=stock_info_payload, timeout=30)
        response.raise_for_status()
        result = response.json()["message"]
        return result
    except httpx.RequestError as e:
        return f"Error during stock update request: {e}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error during stock update request: {e}"


