FROM python:3.12-slim

WORKDIR /app

RUN pip install gunicorn==23.0.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["sh", "-c", "python3 manage.py migrate && gunicorn --bind 0.0.0.0:8000 chatbot_promotion.wsgi"]