from fastapi import FastAPI, HTTPException
from data_access_layer import data_access_layer
from models import UserLoginOrRegistrationRequest, UpdateStockRequest, MonitoredStocks
from stock_market_database import validate_stock_info, register_user, login_user

app = FastAPI()

@app.get("/")
def root():
    return {"Message": "Service is running!"}

@app.post('/Login')
def login_endpoint(request: UserLoginOrRegistrationRequest):
    print("login_endpoint is called 2")
    try:
        result = login_user(request.email, request.password)
        return {"Message": result}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"Message": "An error occurred during login, please try again later."}

@app.post('/Register')
def registration_endpoint(request: UserLoginOrRegistrationRequest):
    print("registration_endpoint called")
    try:
        result = register_user(request.email, request.password)
        return {"Message": "Registration successful. Please log in."}
    except ValueError as ve:
        return {"Message": str(ve)}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"Message": "An error occurred during registration, please try again later."}

@app.post("/update_or_insert_stock")
def update_or_insert_stock_route(request: UpdateStockRequest):
    print("update_or_insert_stock_route called")
    try:
        validate_stock_info(request.stock_info)
    except ValueError as e:
        return {"message": "Incorrect values, please try again!"}
    try:
        data_access_layer.upsert_stock(request.email, request.stock_info)
        return {"message": "Stock information updated or inserted successfully"}
    except Exception as e:
        return {"message": "An error occurred while updating stock information. Please try again later."}

@app.post("/display_current_stocks")
def display_current_stocks(request: MonitoredStocks):
    return data_access_layer.get_stocks(request.email)
    