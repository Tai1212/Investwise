from fastapi import FastAPI, HTTPException
from stock_market_database import (
    register_user,
    user_login,
    update_or_insert_stock
)
from models import UserLoginOrRegistrationRequest, UpdateStockRequest

app = FastAPI()

@app.get("/")
def root():
    return {"Message": "Service is running!"}

@app.post('/Login')
def login_endpoint(request: UserLoginOrRegistrationRequest):
    print("login_endpoint is called")
    try:
        result = user_login(request.email, request.password)
        return {"Message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error")

@app.post('/Register')
def registration_endpoint(request: UserLoginOrRegistrationRequest):
    print("registration_endpoint called")
    try:
        result = register_user(request.email, request.password)
        return {"Message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error")

@app.post("/update_or_insert_stock")
def update_or_insert_stock_route(request: UpdateStockRequest):
    try:
        update_or_insert_stock(request.email, request.stock_info)
        return {"message": "Stock information updated or inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error")

