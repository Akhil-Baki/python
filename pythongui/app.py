from flask import Flask, render_template, request, send_file
import os
import fitz  # PyMuPDF
from gtts import gTTS
import pyttsx3
from docx import Document
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_text(file_path):
    if file_path.endswith('.pdf'):
        doc = fitz.open(file_path)
        text = ''.join([page.get_text() for page in doc])
        doc.close()
        return text.strip()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    return ""


def convert_text_to_speech(text, mode='online', lang='en'):
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    if mode == 'offline':
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    else:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)

    return output_path


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        tts_mode = request.form.get('mode', 'online')
        lang = request.form.get('lang', 'en')

        if not file:
            return render_template('index.html', error="No file uploaded")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.pdf', '.docx']:
            return render_template('index.html', error="Invalid file type")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        text = extract_text(file_path)
        if not text:
            return render_template('index.html', error="No readable text found")

        output_path = convert_text_to_speech(text, mode=tts_mode, lang=lang)
        return render_template('index.html', download=output_path)

    return render_template('index.html')


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
