FROM rasa/rasa:3.6.2-full

WORKDIR /app

COPY . .

# Exponer API con CORS abierto y puerto 8080
CMD ["run", "--enable-api", "--cors", "*", "--port", "8080"]

