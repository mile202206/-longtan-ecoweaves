# -*- coding: utf-8 -*-
"""屏南龙潭非遗数字化年轻化平台 - Flask后端"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session, flash
from functools import wraps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.secret_key = 'longtan_ecoweaves_secret_2024!@#'

# 演示账号（运营人员登录用）
ADMIN_USERNAME = 'ecoweaves'
ADMIN_PASSWORD = 'Longtan@2024'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== 认证路由 ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """后台登录页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html', error=None)


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('login'))


# ==================== 数据存储 ====================

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site_data.json')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS


def load_data():
    """加载站点数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'contents': {},
        'uploads': [],
        'heritage_items': [],
        'music_items': []
    }


def save_data(data):
    """保存站点数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== 页面路由 ====================

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)


@app.route('/heritage')
def heritage():
    data = load_data()
    return render_template('heritage.html', data=data)


@app.route('/music-innovation')
def music_innovation():
    data = load_data()
    return render_template('music-innovation.html', data=data)


@app.route('/admin')
@login_required
def admin():
    data = load_data()
    return render_template('admin.html', data=data, admin_user=session.get('admin_user', ''))


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ==================== 静态资源 ====================

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== 后台API：文案管理 ====================

@app.route('/api/content', methods=['GET'])
def get_content():
    """获取所有页面文案内容"""
    data = load_data()
    return jsonify(data.get('contents', {}))


@app.route('/api/content/<key>', methods=['GET'])
def get_content_item(key):
    """获取指定key的文案"""
    data = load_data()
    contents = data.get('contents', {})
    return jsonify({'key': key, 'value': contents.get(key, '')})


@app.route('/api/content/<key>', methods=['POST'])
def update_content(key):
    """更新指定key的文案"""
    data = load_data()
    if 'contents' not in data:
        data['contents'] = {}
    value = request.json.get('value', '')
    data['contents'][key] = value
    save_data(data)
    return jsonify({'success': True, 'key': key, 'value': value})


@app.route('/api/content', methods=['POST'])
def batch_update_content():
    """批量更新文案"""
    updates = request.json.get('updates', {})
    data = load_data()
    if 'contents' not in data:
        data['contents'] = {}
    for key, value in updates.items():
        data['contents'][key] = value
    save_data(data)
    return jsonify({'success': True, 'updated': list(updates.keys())})


# ==================== 后台API：素材上传 ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图片或视频素材"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '不支持的文件格式'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex[:12]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    category = request.form.get('category', 'general')
    description = request.form.get('description', '')

    data = load_data()
    upload_record = {
        'id': uuid.uuid4().hex[:12],
        'original_name': file.filename,
        'filename': unique_name,
        'url': f'/uploads/{unique_name}',
        'type': 'image' if ext in ALLOWED_IMAGE_EXTENSIONS else 'video',
        'category': category,
        'description': description,
        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    data['uploads'].append(upload_record)
    save_data(data)

    return jsonify({'success': True, 'file': upload_record})


@app.route('/api/uploads', methods=['GET'])
def get_uploads():
    """获取已上传素材列表"""
    data = load_data()
    category = request.args.get('category')
    uploads = data.get('uploads', [])
    if category:
        uploads = [u for u in uploads if u.get('category') == category]
    return jsonify(uploads)


@app.route('/api/uploads/<file_id>', methods=['DELETE'])
def delete_upload(file_id):
    """删除已上传素材"""
    data = load_data()
    uploads = data.get('uploads', [])
    target = next((u for u in uploads if u['id'] == file_id), None)
    if not target:
        return jsonify({'success': False, 'error': '文件不存在'}), 404

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], target['filename'])
    if os.path.exists(filepath):
        os.remove(filepath)

    data['uploads'] = [u for u in uploads if u['id'] != file_id]
    save_data(data)
    return jsonify({'success': True})


# ==================== 后台API：非遗内容管理 ====================

@app.route('/api/heritage', methods=['GET'])
def get_heritage_items():
    """获取非遗介绍列表"""
    data = load_data()
    return jsonify(data.get('heritage_items', []))


@app.route('/api/heritage', methods=['POST'])
def add_heritage_item():
    """新增非遗介绍"""
    item = request.json
    item['id'] = uuid.uuid4().hex[:12]
    item['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = load_data()
    if 'heritage_items' not in data:
        data['heritage_items'] = []
    data['heritage_items'].append(item)
    save_data(data)
    return jsonify({'success': True, 'item': item})


@app.route('/api/heritage/<item_id>', methods=['PUT'])
def update_heritage_item(item_id):
    """编辑非遗介绍"""
    updates = request.json
    data = load_data()
    items = data.get('heritage_items', [])
    for i, item in enumerate(items):
        if item['id'] == item_id:
            items[i].update(updates)
            items[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    data['heritage_items'] = items
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/heritage/<item_id>', methods=['DELETE'])
def delete_heritage_item(item_id):
    """删除非遗介绍"""
    data = load_data()
    data['heritage_items'] = [i for i in data.get('heritage_items', []) if i['id'] != item_id]
    save_data(data)
    return jsonify({'success': True})


# ==================== 后台API：音乐创新内容管理 ====================

@app.route('/api/music', methods=['GET'])
def get_music_items():
    """获取音乐创新列表"""
    data = load_data()
    return jsonify(data.get('music_items', []))


@app.route('/api/music', methods=['POST'])
def add_music_item():
    """新增音乐创新内容"""
    item = request.json
    item['id'] = uuid.uuid4().hex[:12]
    item['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = load_data()
    if 'music_items' not in data:
        data['music_items'] = []
    data['music_items'].append(item)
    save_data(data)
    return jsonify({'success': True, 'item': item})


@app.route('/api/music/<item_id>', methods=['PUT'])
def update_music_item(item_id):
    """编辑音乐创新内容"""
    updates = request.json
    data = load_data()
    items = data.get('music_items', [])
    for i, item in enumerate(items):
        if item['id'] == item_id:
            items[i].update(updates)
            items[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    data['music_items'] = items
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/music/<item_id>', methods=['DELETE'])
def delete_music_item(item_id):
    """删除音乐创新内容"""
    data = load_data()
    data['music_items'] = [i for i in data.get('music_items', []) if i['id'] != item_id]
    save_data(data)
    return jsonify({'success': True})


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=5000)
