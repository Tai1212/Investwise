from pymongo.errors import CollectionInvalid
from pymongo import MongoClient
from pydantic import BaseModel
import logging

logging.root.setLevel(logging.INFO)

client = MongoClient("mongodb://mongo-example:27017")
db = client["stock_market_db"]
try:
    db.create_collection("users")
except CollectionInvalid:
    pass
collection = db["users"]

class StockInformation(BaseModel):
    stock_symbol: str
    purchase_price: float
    target_percentage_change_up: float 
    target_percentage_change_down: float

#logging updates or changes to the database
def print_db_to_log():
    logging.info('stock_market_database: Database names: {}'.format(client.list_database_names()))
    logging.info('stock_market_database:  Collection names: {}'.format(db.list_collection_names()))
    for user in db.users.find():
        logging.info('stock_market_database: User: {}'.format(user))

print_db_to_log()

def register_user(email: str, password: str):
    try:
        existing_user = collection.find_one({"user_email": email})
        if existing_user:
            print("Username already exists. Please choose a different username.")
            return "Username already exists. Please choose a different username."
        else:
            new_user = {"user_email": email, "user_password": password}
            collection.insert_one(new_user)
            print("User registered successfully!")
            print_db_to_log()
            return "User registered successfully!"
    except Exception as e:
        print("An exception occured: ", e)

def user_login(email: str, password: str):
    try:
        user_data = collection.find_one({"user_email": email})
        if user_data:
            if user_data["user_password"] == password:
                print("Login successful!")
                print_db_to_log()
                return "Login successful!"
            else:
                print("Incorrect password.")
                return "Incorrect password."
        else:
            print("User not found")
            return "User not found"
    except Exception as e:
        print("An exception occured: ", e)    

def update_or_insert_stock(user_email: str, stock_info: StockInformation):
    if stock_info.target_percentage_change_down > 0 or stock_info.target_percentage_change_up < 0:
        raise ValueError("Invalid Value! Please try again.")
    stock_data = {
            "stock_symbol": stock_info.stock_symbol,
            "purchase_price": stock_info.purchase_price,
            "target_percentage_change_down": stock_info.target_percentage_change_down,
            "target_percentage_change_up": stock_info.target_percentage_change_up
        }
    user = collection.find_one({"user_email": user_email})
    
    if user:
        stocks = user.setdefault("stocks", [])
        existing_stock = None
        for stock in stocks:
            if stock["stock_symbol"] == stock_info.stock_symbol:
                existing_stock = stock
        if existing_stock:
            existing_stock.update(stock_data)
        else:
            stocks.append(stock_data)
        collection.update_one({"user_email": user_email}, {"$set": {"stocks": stocks}})
        logging.info("stock updated for user {}".format(user_email))
        print_db_to_log()
    else:
        collection.insert_one({"user_email": user_email}, {"stocks": [stock_data]})
        logging.info("stock inserted for user {}".format(user_email))
        print_db_to_log()

def update_user_targets_if_met(user_email: str, stock_symbol: str, target_type: str):
    user = collection.find_one({"user_email": user_email})
    if user:
        stocks = user.get("stocks", [])
        for stock in stocks:
            if stock["stock_symbol"] == stock_symbol:
                if target_type == "up":
                    stock["target_percentage_change_up"] += 10
                elif target_type == "down":
                    stock["target_percentage_change_down"] -= 10
        collection.update_one({"user_email": user_email}, {"$set": {"stocks": stocks}})

