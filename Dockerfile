FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install

CMD ["python3", "main.py"]
