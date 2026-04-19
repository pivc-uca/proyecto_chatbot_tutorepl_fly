FROM python:3.10-slim

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . .

# Definimos la variable para que el código la lea
ENV PORT=8080

# Informamos a Docker qué puerto usa nuestra app
EXPOSE 8080

# 3. Usamos la variable en el comando de inicio. Usamos gunicorn para que escuche en 0.0.0.0 y soporte múltiples conexiones
# Así, si mañana cambias el ENV, no tienes que cambiar el CMD
#CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app"]
CMD gunicorn --bind 0.0.0.0:$PORT app:app
