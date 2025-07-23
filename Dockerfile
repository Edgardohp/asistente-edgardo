# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto por defecto (no usado directamente pero requerido en algunas plataformas)
EXPOSE 8000

# Comando para iniciar el bot de Telegram
CMD ["python", "bot.py"]

