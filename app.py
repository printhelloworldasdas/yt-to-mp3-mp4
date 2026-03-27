import os
import glob
from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Configuración de carpetas temporales para Render
DOWNLOAD_FOLDER = '/tmp'
FFMPEG_PATH = '/opt/render/project/src/ffmpeg/ffmpeg'


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
        # BUG FIX: quality must be a valid resolution number for video; guard against
        # audio-only values like '320' or '128' being passed as height filters.
        valid_video_qualities = {'1080', '720', '480', '360', '240', '144'}
        q_filter = f'[height<={quality}]' if quality in valid_video_qualities else ''
        ydl_opts.update({
            'format': f'bestvideo{q_filter}+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_filename = ydl.prepare_filename(info)

            if format_type == 'mp3':
                # prepare_filename gives the pre-conversion name; swap extension
                final_file = os.path.splitext(temp_filename)[0] + '.mp3'
            else:
                # BUG FIX: yt-dlp may merge into .mp4 even if prepare_filename
                # returns .webm or .mkv. Search for the actual output file.
                base = os.path.splitext(temp_filename)[0]
                # Try the declared name first, then look for any mp4 with that base
                if os.path.exists(base + '.mp4'):
                    final_file = base + '.mp4'
                else:
                    # Fallback: find the newest mp4 in /tmp
                    candidates = glob.glob(f'{DOWNLOAD_FOLDER}/*.mp4')
                    if not candidates:
                        return jsonify({"error": "No se encontró el archivo MP4 generado"}), 500
                    final_file = max(candidates, key=os.path.getmtime)

            if not os.path.exists(final_file):
                return jsonify({"error": f"Archivo no encontrado: {final_file}"}), 500

            # BUG FIX: Clean up the temp file after the response is sent
            # so /tmp doesn't fill up on Render's free tier.
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(final_file)
                except Exception:
                    pass
                return response

            return send_file(final_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
