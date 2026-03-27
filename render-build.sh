#!/usr/bin/env bash
set -o errexit

# 1. Instalar librerías de Python
pip install -r requirements.txt

# 2. Crear carpeta para FFmpeg si no existe
mkdir -p ffmpeg
cd ffmpeg

# 3. Descargar FFmpeg (static build para Linux amd64)
# BUG FIX: La URL anterior apuntaba a la homepage, no al archivo binario.
# Usamos la URL correcta del release estático más reciente.
echo "Descargando FFmpeg..."
curl -L -o ffmpeg-release-amd64-static.tar.xz \
  "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

# 4. Descomprimir con cuidado
# BUG FIX: El nombre del archivo ahora coincide con el que descargamos arriba.
echo "Descomprimiendo..."
tar xf ffmpeg-release-amd64-static.tar.xz --strip-components 1

# 5. Limpiar el archivo descargado para ahorrar espacio
rm ffmpeg-release-amd64-static.tar.xz

cd ..
echo "FFmpeg instalado correctamente en $(pwd)/ffmpeg/ffmpeg"
