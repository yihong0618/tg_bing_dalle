FROM python:3.10-alpine
RUN apk add --no-cache git
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache
COPY *.py .

# Entrypoint script
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Default env vars
ENV tg_token=${tg_token:-}
ENV bing_cookie=${bing_cookie:-}

ENTRYPOINT ["/app/entrypoint.sh"]
