from pydantic import BaseModel

class UserLoginOrRegistrationRequest(BaseModel):
    email: str
    password: str

class StockInformation(BaseModel):
    stock_symbol: str
    purchase_price: float
    last_monitored_percentage_change: float
    target_percentage_change_up: float
    target_percentage_change_down: float

class UpdateStockRequest(BaseModel):
  email: str
  stock_info: StockInformation

class MonitoredStocks(BaseModel):
   email: str




