FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RASA SDK levanta el servidor de acciones
CMD ["rasa", "run", "actions", "--port", "8080"]
