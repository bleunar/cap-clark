FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6100

CMD ["gunicorn", "--bind", "0.0.0.0:6100", "run:app"]