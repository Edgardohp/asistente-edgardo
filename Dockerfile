# Usa una imagen oficial de Python como base
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias del archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en caso de que luego quieras usar FastAPI o similar
EXPOSE 8080

# Comando para ejecutar tu bot de Telegram
CMD ["python", "bot.py"]
