from flask import Flask, render_template, jsonify, request, send_from_directory, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge
import logging
import uuid
import os
from io import BytesIO
from pathlib import Path

app = Flask(__name__)


BASE_DIR = Path(__file__).resolve().parent

IMAGES_DIR = Path(os.getenv('IMAGES_DIR', BASE_DIR / 'images'))

LOGS_DIR = Path(os.getenv('LOGS_DIR', BASE_DIR / 'logs'))

MAX_FILE_SIZE = 5 * 1024 * 1024

REQUEST_OVERHEAD = 256 * 1024

REQUEST_LIMIT = MAX_FILE_SIZE +  REQUEST_OVERHEAD

ALLOWED_IMAGE_FORMATS = {
    'JPEG' : 'jpg',
    'PNG' : 'png',
    'GIF' : 'gif'
}

app.config['MAX_CONTENT_LENGTH'] = REQUEST_LIMIT

IMAGES_DIR.mkdir(exist_ok=True)

LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / 'app.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def detect_image_extension(file_data: bytes):
    try:
        with Image.open(BytesIO(file_data)) as image:
            image.verify()
            return ALLOWED_IMAGE_FORMATS.get(image.format)

    except (UnidentifiedImageError, OSError):
        return None




@app.get('/')
def home():
    return render_template('index.html')

@app.get('/upload')
def upload_page():
    return render_template('upload.html')


@app.post('/upload')
def upload_image():
    uploaded_file = request.files.get('image')
    if uploaded_file is None:
        logging.warning('Ошибка: файл не найден в запросе')
        return jsonify({
            'error': 'Файл не найден'
        })

    original_filename = uploaded_file.filename or 'unknown'

    file_data = uploaded_file.read()

    if not file_data:
        logging.warning(f'Пустой файл {original_filename}' )
        return jsonify({
            'error': 'Файл пустой'
        }), 400

    if len(file_data) > MAX_FILE_SIZE:
        logging.warning(f'Ошибка {original_filename} не должет быть больше 5 МБайт')
        return jsonify({
            'error': 'Файт не должен быть больше 5Мбайт'
        }), 400

    image_extension = detect_image_extension(file_data)

    if image_extension is None:
        logging.warning(f'Ошибка: файл {original_filename} не поддерживается или пустой')
        return jsonify({
            'error': 'Поддерживаются только форматы jpg, png, gif'
        })

    unique_filename = f'{uuid.uuid4().hex}.{image_extension}'

    target_save_path = IMAGES_DIR / unique_filename

    target_save_path.write_bytes(file_data)

    relative_url = url_for('get_image', filename=unique_filename)
    full_url = request.host_url.rstrip('/') + relative_url

    logging.info(f'Успех. Изображение загружено как {original_filename}')
    return jsonify({
        'message': 'Изображение успешно загружено',
        'id': unique_filename,
        'url': relative_url,
        'full_url': full_url
    }), 201


@app.get('/images/<path:filename>')
def get_image(filename):
    return send_from_directory(IMAGES_DIR, filename)



@app.get('/images')
def images_page():

    images = []

    for image_path in sorted(IMAGES_DIR.iterdir(), key=lambda path:path.stat().st_mtime, reverse=True):
        if not image_path.is_file():
            continue

        relative_url = url_for('get_image', filename=image_path.name)
        full_url = request.host_url.rstrip('/') + relative_url

        images.append(
            {
                'name': image_path.name,
                'url': relative_url,
                'full_url': full_url

            }
        )

    return render_template('images.html', images=images)


if __name__ == '__main__':
    app.run(debug=True)