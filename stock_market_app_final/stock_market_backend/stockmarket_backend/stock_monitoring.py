from pymongo import MongoClient
import requests
import smtplib
from email.mime.text import MIMEText
from stock_market_database import update_user_targets_if_met
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

logging.root.setLevel(logging.INFO)
client = MongoClient("mongodb://mongo-example:27017")
db = client["stock_market_db"]
collection = db["users"]

#logging information in the database
logging.info('stock_monitoring: database names: {}'.format(client.list_database_names()))
logging.info('stock_monitoring: collection names: {}'.format(db.list_collection_names()))
logging.info('stock_monitoring: stocks: {}'.format( db.users.find_one()))

class EmailNotification:
    def __init__(self, sender, password):
        self.sender = sender
        self.password = password
    
    def send_email(self, subject, body, recipient):
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = recipient

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(self.sender, self.password)
                smtp_server.sendmail(self.sender, recipient, message.as_string())
            print("Message Sent!")
        except Exception as e:
            print("An error occurred:", e)

def get_current_stock_price(stock_symbol: str, api_key="CM0EOVWPS7EZ58J9") -> float:
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price_data = data["Global Quote"]["05. price"]
            return price_data
    except Exception as e:
        print("An error occurred:", e)

def calculate_percentage_change(stock_symbol: str, purchase_price: float) -> float:
    current_price = float(get_current_stock_price(stock_symbol))
    if purchase_price == 0:
         return None
    else: 
        percentage_change = ((current_price - purchase_price) / purchase_price) * 100
        return percentage_change
    
def get_user_stocks(user_email: str) -> list:
    user_data = collection.find_one({"user_email": user_email})
    if user_data:
        return user_data.get("stocks", [])
    else:
        return []

def write_email_body(stock_targets_met: list) -> str:
    body = "Hello,\n\n"
    body += "The following stocks in your account have met their target:\n\n"
    for stock in stock_targets_met:
        stock_symbol = stock['stock_symbol']
        percentage_change = "{:.2f}".format(stock['percentage_change'])
        body += f"Stock Symbol: {stock_symbol}\n"
        body += f"Percentage Change: {percentage_change}%\n\n"
    body += "For each target met, we have adjusted the target value in your account by 10%. Thank you for using InvestWise!\n"
    return body

def send_notification_email(user_email: str, stock_targets_met: list):
    subject = "Stock Target Reached!"
    body = write_email_body(stock_targets_met)
    email_sender = EmailNotification(sender="stockmarketapp123@gmail.com", password="xkrq lpwf hxfm qgeh")
    email_sender.send_email(subject=subject, body=body, recipient=user_email) 

def append_stock_targets_met_list(stock_targets_met: list, stock: dict, user_email: str):
    stock_symbol = stock["stock_symbol"]
    percentage_change = calculate_percentage_change(stock_symbol, stock["purchase_price"])
    if stock["target_percentage_change_up"] <= percentage_change:
        logging.info("stock target change up for {}. percentage_change={}.".format(stock_symbol, percentage_change))
        stock_targets_met.append({"stock_symbol": stock_symbol, "percentage_change": percentage_change, "target_type": "up"})
    if stock["target_percentage_change_down"] >= percentage_change:
        logging.info("stock target change down for {}. percentage_change={}.".format(stock_symbol, percentage_change))
        stock_targets_met.append({"stock_symbol": stock_symbol, "percentage_change": percentage_change, "target_type": "down"})

def monitoring_user_stock_preferences():
    notification_sent = False
    for user_data in collection.find():
        user_email = user_data["user_email"]
        user_stocks = get_user_stocks(user_email)
        stock_targets_met = []
        for stock in user_stocks:
            append_stock_targets_met_list(stock_targets_met, stock, user_email)
        if len(stock_targets_met) > 0:
            send_notification_email(user_email, stock_targets_met)
            logging.info("Sending notification for user_email {} with stocks {}".format(user_email, stock_targets_met))
            notification_sent = True
            for stock_info in stock_targets_met:
                update_user_targets_if_met(user_email, stock_info["stock_symbol"], stock_info["target_type"])
    if notification_sent:
        logging.info("Notification sent")
    else:
        logging.info("Notification not sent")

#Function to run the stock monitoring function one time every day. 
def run_every_day(job_function):
    scheduler = BlockingScheduler()
    first_run_time = datetime.now() + timedelta(seconds=300)
    scheduler.add_job(job_function, 'cron', day_of_week='*', hour=first_run_time.hour, minute=first_run_time.minute, second=first_run_time.second)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

run_every_day(monitoring_user_stock_preferences)
