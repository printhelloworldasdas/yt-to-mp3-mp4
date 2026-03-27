#!/usr/bin/env bash
set -o errexit

# Instalar dependencias de Python
pip install -r requirements.txt

# Descargar FFmpeg estático
mkdir -p ffmpeg
cd ffmpeg
curl -L https://johnvansickle.com | tar xJ --strip-components 1
cd ..

