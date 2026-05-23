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
app.secret_key = os.environ.get('LONGTAN_SECRET_KEY', 'longtan_ecoweaves_secret_2024!@#')

# 演示账号（运营人员登录用）—— 支持环境变量覆盖
ADMIN_USERNAME = os.environ.get('LONGTAN_ADMIN_USER', 'ecoweaves')
ADMIN_PASSWORD = os.environ.get('LONGTAN_ADMIN_PASS', 'Longtan@2024')


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
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[WARN] 加载数据失败: {e}")
    return {
        'contents': {},
        'uploads': [],
        'heritage_items': [],
        'music_items': []
    }


def save_data(data):
    """保存站点数据（原子写入，防止并发覆盖）"""
    import tempfile
    temp_name = None
    try:
        dir_name = os.path.dirname(DATA_FILE)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=dir_name, delete=False) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            temp_name = f.name
        os.replace(temp_name, DATA_FILE)
    except (IOError, OSError) as e:
        print(f"[ERROR] 保存数据失败: {e}")
        if temp_name and os.path.exists(temp_name):
            os.remove(temp_name)


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


@app.route('/offline-space')
def offline_space():
    data = load_data()
    return render_template('offline-space.html', data=data)


@app.route('/creative')
def creative():
    data = load_data()
    return render_template('creative.html', data=data)


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ==================== 静态资源 ====================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== API：文件上传 ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图片或视频素材"""
    try:
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
    except (IOError, OSError) as e:
        print(f"[ERROR] 文件上传失败: {e}")
        return jsonify({'success': False, 'error': '文件保存失败'}), 500


# ==================== API：文件删除 ====================

@app.route('/api/uploads/<file_id>', methods=['DELETE'])
def delete_upload(file_id):
    """删除已上传素材"""
    try:
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
    except (IOError, OSError) as e:
        print(f"[ERROR] 删除文件失败: {e}")
        return jsonify({'success': False, 'error': '删除失败'}), 500


# ==================== API：非遗内容管理 ====================

@app.route('/api/heritage', methods=['GET'])
def get_heritage_items():
    """获取非遗介绍列表"""
    try:
        data = load_data()
        return jsonify(data.get('heritage_items', []))
    except Exception as e:
        print(f"[ERROR] 获取非遗列表失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500


@app.route('/api/heritage', methods=['POST'])
def add_heritage_item():
    """新增非遗介绍"""
    try:
        item = request.json
        item['id'] = uuid.uuid4().hex[:12]
        item['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = load_data()
        if 'heritage_items' not in data:
            data['heritage_items'] = []
        data['heritage_items'].append(item)
        save_data(data)
        return jsonify({'success': True, 'item': item})
    except Exception as e:
        print(f"[ERROR] 新增非遗失败: {e}")
        return jsonify({'success': False, 'error': '新增失败'}), 500


@app.route('/api/heritage/<item_id>', methods=['PUT'])
def update_heritage_item(item_id):
    """编辑非遗介绍"""
    try:
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
    except Exception as e:
        print(f"[ERROR] 编辑非遗失败: {e}")
        return jsonify({'success': False, 'error': '编辑失败'}), 500


@app.route('/api/heritage/<item_id>', methods=['DELETE'])
def delete_heritage_item(item_id):
    """删除非遗介绍"""
    try:
        data = load_data()
        data['heritage_items'] = [i for i in data.get('heritage_items', []) if i['id'] != item_id]
        save_data(data)
        return jsonify({'success': True})
    except Exception as e:
        print(f"[ERROR] 删除非遗失败: {e}")
        return jsonify({'success': False, 'error': '删除失败'}), 500


# ==================== API：音乐创新管理 ====================

@app.route('/api/music', methods=['GET'])
def get_music_items():
    """获取音乐创新列表"""
    try:
        data = load_data()
        return jsonify(data.get('music_items', []))
    except Exception as e:
        print(f"[ERROR] 获取音乐列表失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500


@app.route('/api/music', methods=['POST'])
def add_music_item():
    """新增音乐创新内容"""
    try:
        item = request.json
        item['id'] = uuid.uuid4().hex[:12]
        item['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = load_data()
        if 'music_items' not in data:
            data['music_items'] = []
        data['music_items'].append(item)
        save_data(data)
        return jsonify({'success': True, 'item': item})
    except Exception as e:
        print(f"[ERROR] 新增音乐创新失败: {e}")
        return jsonify({'success': False, 'error': '新增失败'}), 500


@app.route('/api/music/<item_id>', methods=['PUT'])
def update_music_item(item_id):
    """编辑音乐创新内容"""
    try:
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
    except Exception as e:
        print(f"[ERROR] 编辑音乐创新失败: {e}")
        return jsonify({'success': False, 'error': '编辑失败'}), 500


@app.route('/api/music/<item_id>', methods=['DELETE'])
def delete_music_item(item_id):
    """删除音乐创新内容"""
    try:
        data = load_data()
        data['music_items'] = [i for i in data.get('music_items', []) if i['id'] != item_id]
        save_data(data)
        return jsonify({'success': True})
    except Exception as e:
        print(f"[ERROR] 删除音乐创新失败: {e}")
        return jsonify({'success': False, 'error': '删除失败'}), 500


# ==================== 启动服务 ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
