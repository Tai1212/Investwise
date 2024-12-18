FROM python:3.10

COPY ./requirements.txt .

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8001

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8001 --reload & python stock_monitoring.py"]
