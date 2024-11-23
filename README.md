# Investwise

Welcome to Investwise, your personalized stock monitoring app designed to keep you informed about the performance of your selected stocks. With this app, you can effortlessly track the fluctuations of your favorite stocks in real-time, receiving timely notifications whenever they rise or fall by a specified percentage. 

## Architecture
![alt text](docs/architecture.png | width=100)

## Features

### 1. Login:
- Existing users can log into their account. 
- Non existing users trying to log in will be notified that their credentials are invalid.

### 2. Registration:
- New users can create an account by inputting an email and passsword. 

### 3. Inserting or Updating Stock Preferences:
- **Insert New Stock:** Insert any stock, the price you purchased it, and your prefered percentage change.
- **Update existing Stock:** If the stock symbol already exists, we will update the database with the new preferences. 

### 4. Target Met Notification:
- When at least one of the users stocks met their desired target change, an email will be sent to the email address. 
- After the notification is sent, the specific stock's target that was met will be automatically adjusted by 10% in the database.

### 5. View Stocks:
- The user can request to view their current stock portfolio. 
- The last checked stock price will be shown in addition to the stock symbol, user percentage preferences, and the user's purchase price of the stock.

## User Interfaces

### 1. TelegramUI:
- The user can connect to telegram to access their Investwise account by typing '/start' and inputting the secret passcode
- This is an easy way for the user to connect to the app easily and on the go.

## 2. Graphic UI:
- The user can connect to the graphic user interface to interact with the investwise account. 

## Getting Started

### Building the Application

1. **Clone the Repository:**
   ```bash
   #to do: add repository name in github
   ```

2. **Install Docker Desktop:**
   If you don't have Docker Desktop installed, you can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).

3. **Navigate to the cloned directory:**
    ```bash
    cd investwise
    cd .\stock_market_app_final\
    cd .\stock_market_backend\
   ```

4. **Run this command to start the application's containers:**
   ```bash
   docker-compose -f .\docker-compose.yml up -d
   ```

## Accessing the Application

Once the Docker container is up and running, access Investwise's website by visiting the following link: #TODO: add proper GUI link# in your web browser.

Feel free to explore and join Investwise!

For more details, issues, or contributions, please check out our [GitHub repository]
#(to - do: add github repository).

## Demo

Check out the [YouTube video](https://youtu.be/TBjLobCB_6k) for a demo.
