import logging
import requests
from data_access_layer import data_access_layer
from models import StockInformation

def login_user(email: str, password: str) -> bool:
    return data_access_layer.get_user_password(email) == password

def register_user(email: str, password: str) -> bool:
    if data_access_layer.does_user_exist(email):
        logging.info("register_user: user already exists")
        raise ValueError("Username already exists, please try a different one.")
    else:
        logging.info("register_user: succeeded")
        data_access_layer.create_user(email, password)
        return True

#check if the stock_symbol entered by the user is valid using alpha vantage API
def verify_stock_symbol(stock_symbol: str, api_key="PGEB6H81H9XJS4ZP"):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            logging.info("verify_stock_symbol returns true")
            return True
        logging.info("verify_stock_symbol got unexpected format for stock {} format={}".format(stock_symbol, data))  
        return False
    except requests.RequestException as e:
        logging.info("verify_stock_symbol exception raised e={}".format(str(e)))
        return False

def update_user_targets_if_met(user_email: str, stock_symbol: str, target_type: str):
    if target_type == "up":
        current_target = data_access_layer.get_target_percentage_change_up(user_email, stock_symbol)
        data_access_layer.update_target_percentage_change_up(user_email, stock_symbol, current_target + 10)
    elif target_type == "down":
        current_target = data_access_layer.get_target_percentage_change_down(user_email, stock_symbol)
        data_access_layer.update_target_percentage_change_down(user_email, stock_symbol, current_target - 10)

def validate_stock_info(stock_info: StockInformation):
    if not verify_stock_symbol(stock_info.stock_symbol):
        logging.info("Invalid Stock Symbol! Please try again.")
        raise ValueError("Invalid Stock Symbol! Please try again.")
    if stock_info.target_percentage_change_down > 0 or stock_info.target_percentage_change_up < 0:
        logging.info("Invalid Value! Please try again.")
        raise ValueError("Invalid Value! Please try again.")


    
