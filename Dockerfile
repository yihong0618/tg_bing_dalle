FROM python:3.10 AS builder
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv .venv && .venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY tg.py .

ENV tg_token=$tg_token
ENV bing_cookie=$bing_cookie

CMD .venv/bin/python3 tg.py $tg_token "$bing_cookie"
