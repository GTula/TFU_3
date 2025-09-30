FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["uvicorn", "presentacion.main:app", "--host", "0.0.0.0", "--port", "8040"]