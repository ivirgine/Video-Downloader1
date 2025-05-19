from flask import Flask, render_template, request, jsonify, send_file
from pytube import YouTube
import os
import tempfile
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form.get('url')
    try:
        yt = YouTube(url)
        thumbnail = yt.thumbnail_url
        title = yt.title
        duration = yt.length
        streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()

        formats = []
        for stream in streams:
            formats.append({
                'itag': stream.itag,
                'res': stream.resolution,
                'filesize': stream.filesize,
                'ext': stream.mime_type.split('/')[-1],
                'proxy_url': f"/download?itag={stream.itag}&url={url}"
            })

        return jsonify({
            'title': title,
            'duration': f"{duration // 60}:{duration % 60:02}",
            'thumbnail': thumbnail,
            'formats': formats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download')
def download():
    url = request.args.get('url')
    itag = request.args.get('itag')
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    stream.download(filename=temp.name)
    return send_file(temp.name, as_attachment=True, download_name=f"{yt.title}.mp4")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
