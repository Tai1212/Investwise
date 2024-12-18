from pymongo import MongoClient
import requests
import smtplib
from email.mime.text import MIMEText
from data_access_layer import data_access_layer
from stock_market_database import update_user_targets_if_met
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

logging.root.setLevel(logging.INFO)

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

def get_current_stock_price(stock_symbol: str, api_key="PGEB6H81H9XJS4ZP") -> float:
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

def append_stock_targets_met_list(stock_targets_met: list, stock: dict, percentage_change: float):
    stock_symbol = stock["stock_symbol"]
    if stock["target_percentage_change_up"] <= percentage_change:
        logging.info("stock target change up for {}. percentage_change={}.".format(stock_symbol, percentage_change))
        stock_targets_met.append({"stock_symbol": stock_symbol, "percentage_change": percentage_change, "target_type": "up"})
    if stock["target_percentage_change_down"] >= percentage_change:
        logging.info("stock target change down for {}. percentage_change={}.".format(stock_symbol, percentage_change))
        stock_targets_met.append({"stock_symbol": stock_symbol, "percentage_change": percentage_change, "target_type": "down"})


def monitoring_user_stock_preferences():
    notification_sent = False
    for user_email in data_access_layer.get_user_emails():
        user_stocks = data_access_layer.get_stocks(user_email)
        stock_targets_met = []
        for stock in user_stocks:
            percentage_change = calculate_percentage_change(stock["stock_symbol"], stock["purchase_price"])
            data_access_layer.update_last_monitored_percentage_change(user_email, stock["stock_symbol"], percentage_change)
            append_stock_targets_met_list(stock_targets_met, stock, percentage_change)
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
