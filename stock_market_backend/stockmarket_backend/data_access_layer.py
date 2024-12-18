from pymongo.errors import CollectionInvalid
from pymongo import MongoClient
import logging
from models import StockInformation

"""
The DAL class provides a simplified interface for interacting with a MongoDB
database to manage user and stock information.
"""
class DAL():
    def __init__(self):
        logging.root.setLevel(logging.INFO)
        self.client = MongoClient("mongodb://mongo-example:27017")
        self.db = self.client["stock_market_db"]
        self.collection_name = "users"
        try:
            self.db.create_collection(self.collection_name)
        except CollectionInvalid:
            pass
        self.collection = self.db[self.collection_name]
    
    def delete_all_users(self):
        try:
            result = self.collection.delete_many({})
            print(f"Deleted {result.deleted_count} documents from {self.collection_name}")
        except Exception as e:
            print(f"Error deleting documents: {str(e)}")
            raise

    # Call does_user_exist before using this function
    def create_user(self, email: str, password: str):
        new_user = {"user_email": email, "user_password": password}
        self.collection.insert_one(new_user) 

    def does_user_exist(self, email) -> bool:
        return self.collection.find_one({"user_email": email}) is not None
        
    def get_user_password(self, email: str) -> str:
        user_data = self.collection.find_one({"user_email": email})
        if not user_data:
            return None
        return user_data["user_password"]
    
    def get_stocks(self, user_email: str) -> list:
        user_data = self.collection.find_one({"user_email": user_email})
        if user_data:
            return user_data.get("stocks", [])
        else:
            return []
            
    def upsert_stock(self, user_email: str, stock_info: StockInformation):
        stock_data = {
                "stock_symbol": stock_info.stock_symbol,
                "purchase_price": stock_info.purchase_price,
                "last_monitored_percentage_change": stock_info.last_monitored_percentage_change,
                "target_percentage_change_down": stock_info.target_percentage_change_down,
                "target_percentage_change_up": stock_info.target_percentage_change_up
            }
        user = self.collection.find_one({"user_email": user_email})
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
            self.collection.update_one({"user_email": user_email}, {"$set": {"stocks": stocks}})
            logging.info("stock updated for user {}".format(user_email))
        else:
            self.collection.insert_one({"user_email": user_email}, {"stocks": [stock_data]})
            logging.info("stock inserted for user {}".format(user_email))

    def update_last_monitored_percentage_change(self, user_email: str, stock_symbol: str, new_value: float):
        self.collection.update_one({"user_email": user_email, "stocks.stock_symbol": stock_symbol}, {"$set":{"stocks.$.last_monitored_percentage_change": new_value}})

    def update_target_percentage_change_up(self, user_email:str, stock_symbol: str, new_value: float):
        self.collection.update_one({"user_email": user_email, "stocks.stock_symbol": stock_symbol}, {"$set":{"stocks.$.target_percentage_change_up": new_value}})

    def update_target_percentage_change_down(self, user_email:str, stock_symbol: str, new_value: float):
        self.collection.update_one({"user_email": user_email, "stocks.stock_symbol": stock_symbol}, {"$set":{"stocks.$.target_percentage_change_down": new_value}})
        
    def get_target_percentage_change_up(self, user_email:str, stock_symbol: str):
        user = self.collection.find_one({"user_email": user_email})
        if user:
            stocks = user.get("stocks", [])
            for stock in stocks:
                if stock["stock_symbol"] == stock_symbol:
                    return stock["target_percentage_change_up"]

    def get_target_percentage_change_down(self, user_email:str, stock_symbol: str):
        user = self.collection.find_one({"user_email": user_email})
        if user:
            stocks = user.get("stocks", [])
            for stock in stocks:
                if stock["stock_symbol"] == stock_symbol:
                    return stock["target_percentage_change_down"]
                
    def get_user_emails(self):
        for user_email in self.collection.find():
            yield user_email["user_email"]

data_access_layer = DAL()