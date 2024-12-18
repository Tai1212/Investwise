from backend_api import perform_login, perform_registration, display_current_stocks, update_or_insert_stock
import os
import telebot
import logging

API_KEY = "7902704625:AAFbtEuduP0eg_ykpVk2iHRbbD0yRQbeVHw"
SECRET_CODE = "1920"

bot = telebot.TeleBot(API_KEY)

# Session state to track login and secret code status
session_state = {}

# Main menu with "secret" button (only available after secret is entered)
main_menu = telebot.types.InlineKeyboardMarkup()
main_menu.add(telebot.types.InlineKeyboardButton(text="Secret Menu", callback_data="secret"))

# Submenu for login and register
auth_menu = telebot.types.InlineKeyboardMarkup()
auth_menu.add(telebot.types.InlineKeyboardButton(text="Login", callback_data="login"))
auth_menu.add(telebot.types.InlineKeyboardButton(text="Register", callback_data="register"))

# Submenu for viewing and managing stocks (only shown if logged in)
stocks_menu = telebot.types.InlineKeyboardMarkup()
stocks_menu.add(telebot.types.InlineKeyboardButton(text="View Stocks", callback_data="view_stocks"))
stocks_menu.add(telebot.types.InlineKeyboardButton(text="Upsert Stock", callback_data="upsert_stock"))

# Handle callback queries (e.g., button clicks from the inline keyboard)
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # Handle "Secret Menu" button
    if call.data == "secret":
        if not session_state.get(call.message.chat.id, {}).get("user_authenticated", False):
            bot.send_message(call.message.chat.id, "Please login or register:", reply_markup=auth_menu)
        else:
            bot.send_message(call.message.chat.id, "You are already logged in.", reply_markup=stocks_menu)
    
    # Handle "Login" button
    elif call.data == "login":
        msg = bot.send_message(call.message.chat.id, "Please enter your email and password (email password):")
        bot.register_next_step_handler(msg, process_login)
    
    # Handle "Register" button
    elif call.data == "register":
        msg = bot.send_message(call.message.chat.id, "Please enter your email and password to register (email password):")
        bot.register_next_step_handler(msg, process_register)
    
    # Handle "View Stocks" button (when logged in)
    elif call.data == "view_stocks" and session_state.get(call.message.chat.id, {}).get("user_authenticated", False):
        process_view_stocks(call.message)
    
    # Handle "Upsert Stock" button (when logged in)
    elif call.data == "upsert_stock" and session_state.get(call.message.chat.id, {}).get("user_authenticated", False):
        msg = bot.send_message(call.message.chat.id, "Enter stock_symbol, price_purchased, target_percentage_up, target_percentage_down (comma-separated):")
        bot.register_next_step_handler(msg, process_upsert_stock)

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to the bot! To access the menu, please enter the secret code.")
    msg = bot.send_message(message.chat.id, "Please enter the secret code to continue:")
    bot.register_next_step_handler(msg, check_secret)

# Retry secret function
def retry_secret(message):
    msg = bot.send_message(message.chat.id, "Please enter the secret code to continue:")
    bot.register_next_step_handler(msg, check_secret)

# Function to check the secret
def check_secret(message):
    if message.text == SECRET_CODE:
        session_state[message.chat.id] = {"secret_entered": True, "user_authenticated": False}
        bot.send_message(message.chat.id, "Secret is correct! Here is the menu:", reply_markup=main_menu)
    else:
        bot.send_message(message.chat.id, "Incorrect secret. Please type /start to try again.")
        retry_secret(message)


# Retry login function
def retry_login(message):
    msg = bot.send_message(message.chat.id, "Please enter your email and password (email password):")
    bot.register_next_step_handler(msg, process_login)

# Login process using backend API
def process_login(message):
    try:
        email, password = message.text.split()
        result = perform_login({"email": email, "password": password})
        if result: 
            session_state[message.chat.id]["user_authenticated"] = True
            session_state[message.chat.id]["email"] = email
            bot.send_message(message.chat.id, f"Login successful for {email}!", reply_markup=stocks_menu)
        else: 
            bot.send_message(message.chat.id, "User does not exist")
            bot.send_message(message.chat.id, "Please try again or register:", reply_markup=auth_menu)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please use 'email password'. Try again.")
        retry_login(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Error occurred")
        retry_login(message)

# Retry register function
def retry_register(message):
    msg = bot.send_message(message.chat.id, "Please enter your email and password to register (email password):")
    bot.register_next_step_handler(msg, process_register)

# Registration process using backend API
def process_register(message):
    try:
        email, password = message.text.split()
        result = perform_registration({"email": email, "password": password})
        if result:
            bot.send_message(message.chat.id, f"Registered successfully with {email}. Please log in.", reply_markup=auth_menu)
        else:
            bot.send_message(message.chat.id, "Registration failed. Try again.")
            retry_register(message)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please use 'email password'. Try again.")
        retry_register(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Error occurred")
        retry_register(message)

# View monitored stocks process
def process_view_stocks(message):
    if session_state.get(message.chat.id, {}).get("user_authenticated", False):
        email = session_state[message.chat.id]["email"]
        try:
            stocks_dict = display_current_stocks({"email": email})
            if stocks_dict is None or len(stocks_dict) == 0:
                bot.send_message(message.chat.id, "No stocks found.")
                return
        except Exception as e:
            bot.send_message(message.chat.id, "Error occurred")
        for stock_symbol, stock_info_list in stocks_dict.items():
            stock_symbol = f"Stock Symbol: {stock_symbol}"
            stock_info = "\n".join(stock_info_list)
            bot.send_message(message.chat.id, "{}\n{}".format(stock_symbol, stock_info))
        bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=stocks_menu)
    else:
        bot.send_message(message.chat.id, "You need to log in to view stocks. Please log in.")

def process_upsert_stock(message):
    if session_state.get(message.chat.id, {}).get("user_authenticated", False):
        try:
            # Directly forward user input to the backend
            stock_symbol, price_purchased, target_percentage_up, target_percentage_down = message.text.split(',')
            
            # Call the backend API to update or insert stock
            result = update_or_insert_stock({
                "email": session_state[message.chat.id]["email"],
                "stock_info": {
                    "stock_symbol": stock_symbol.strip(),
                    "purchase_price": float(price_purchased.strip()),
                    "last_monitored_percentage_change": 0,  # Initial value
                    "target_percentage_change_up": float(target_percentage_up.strip()),
                    "target_percentage_change_down": float(target_percentage_down.strip())
                }
            })

            bot.send_message(message.chat.id, result)
            bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=stocks_menu)

        except Exception as e:
            bot.send_message(message.chat.id, f"Error processing stock data: {e}. Please try again.")
            retry_upsert_stock(message)
    else:
        bot.send_message(message.chat.id, "You need to log in to update or insert stocks. Please log in.")

# Retry upsert stock function
def retry_upsert_stock(message):
    msg = bot.send_message(message.chat.id, "Enter stock_symbol, price_purchased, target_percentage_up, target_percentage_down (comma-separated):")
    bot.register_next_step_handler(msg, process_upsert_stock)

def main():
    logging.info("starting telegram bot")
    bot.polling()
