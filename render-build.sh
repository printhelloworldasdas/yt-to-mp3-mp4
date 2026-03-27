#!/usr/bin/env bash
set -o errexit

# 1. Instalar librerías de Python
pip install -r requirements.txt

# 2. Crear carpeta para FFmpeg si no existe
mkdir -p ffmpeg
cd ffmpeg

# 3. Descargar FFmpeg (Usamos -L para seguir redirecciones y -O para guardar el archivo)
echo "Descargando FFmpeg..."
curl -L -O https://johnvansickle.com

# 4. Descomprimir con cuidado
echo "Descomprimiendo..."
tar xf ffmpeg-release-amd64-static.tar.xz --strip-components 1

# 5. Limpiar el archivo descargado para ahorrar espacio
rm ffmpeg-release-amd64-static.tar.xz

cd ..
echo "FFmpeg instalado correctamente."
