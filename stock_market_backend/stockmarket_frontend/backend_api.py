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

def perform_login(login_request) -> bool:
    api_url = f"{backend_base_url}/Login"
    try:
        logging.info("perform_login calling httpx.post with api_url={}, json={}".format(api_url, login_request))
        response = httpx.post(api_url, json=login_request, timeout=45)
        response.raise_for_status()
        return response.json()["Message"]
    except httpx.RequestError as e:
        raise Exception(f"Error during login request: {e}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error during login request: {e}")
    
def perform_registration(login_request) -> bool:
    api_url = f"{backend_base_url}/Register"
    try:
        response = httpx.post(api_url, json=login_request, timeout=30)
        response.raise_for_status()
        return response.json()['Message']
        
    except httpx.RequestError as e:
        raise Exception(f"Error during registration request: {e}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error during registration request: {e}")
        

def update_or_insert_stock(stock_info_payload) -> str:
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

def generate_stocks_string_for_display(stock) -> list[str]:
    return [f"Purchase Price: ${stock['purchase_price']:.2f}",
        f"Last Monitored Percentage Change: {stock['last_monitored_percentage_change']:.2f}%",
        f"Target Percentage Change Down: {stock['target_percentage_change_down']:.2f}%",
        f"Target Percentage Change Up: {stock['target_percentage_change_up']:.2f}%"]

def display_current_stocks(email) -> dict[list]:
    logging.info("display_current_stocks is called with email={}".format(email))
    api_url = f"{backend_base_url}/display_current_stocks"
    try:
        response = httpx.post(api_url, json=email, timeout=30)
        response.raise_for_status()
        if isinstance(response.json(), list):
            stocks_data = response.json()
            stocks_dict = {}
            for stock in stocks_data:
                stocks_dict[f"{stock['stock_symbol']}"] = generate_stocks_string_for_display(stock)
            return stocks_dict
        else:
            raise Exception(f"Unexpected response format: {response.json()}")
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        raise Exception(f"Error during display stock request: {e}")

