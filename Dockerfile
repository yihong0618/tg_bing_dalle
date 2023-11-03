FROM python:3.10-alpine
RUN apk add --no-cache git
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache
COPY tg.py .

CMD python3 tg.py
