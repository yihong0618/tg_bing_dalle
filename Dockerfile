FROM python:3.10-alpine
RUN apk add --no-cache git
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache
COPY tg.py .

ENV tg_token=$tg_token
ENV bing_cookie=$bing_cookie

CMD python3 tg.py $tg_token $bing_cookie
