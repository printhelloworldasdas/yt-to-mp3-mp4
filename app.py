import os
import subprocess
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Configuración de carpetas temporales para Render
DOWNLOAD_FOLDER = '/tmp'
FFMPEG_PATH = '/opt/render/project/src/ffmpeg/ffmpeg' # Ruta donde lo instalaremos

@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp3')
    quality = request.args.get('quality', 'best')

    if not url:
        return jsonify({"error": "Falta la URL"}), 400

    # Opciones base de yt-dlp
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'ffmpeg_location': FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else 'ffmpeg',
        'noplaylist': True,
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality if quality.isdigit() else '192',
            }],
        })
    else:
        # MP4: Combina mejor video (hasta la calidad elegida) con mejor audio
        q_filter = f'[height<={quality}]' if quality.isdigit() else ''
        ydl_opts.update({
            'format': f'bestvideo{q_filter}+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_filename = ydl.prepare_filename(info)
            
            # Ajustar extensión si es mp3
            if format_type == 'mp3':
                final_file = os.path.splitext(temp_filename)[0] + ".mp3"
            else:
                final_file = temp_filename

            return send_file(final_file, as_attachment=True)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
