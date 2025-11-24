import os
import time
import json
import uuid
from flask import Flask, render_template, request, jsonify, Response

app = Flask(__name__)

# 설정: 업로드된 파일이 저장될 폴더
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 가상 사전 데이터 (Mock DB)
# 예시를 위해 그냥 넣어논거입니다....
MOCK_DICTIONARY = [
    {"id": "wd_01", "word": "안녕하세요 (Hello)", "video_url": "mock_hello.mp4"},
    {"id": "wd_02", "word": "사랑합니다 (Love)", "video_url": "mock_love.mp4"},
    {"id": "wd_03", "word": "감사합니다 (Thank you)", "video_url": "mock_thanks.mp4"},
    {"id": "wd_04", "word": "만나서 반가워요 (Nice to meet you)", "video_url": "mock_meet.mp4"},
    {"id": "wd_05", "word": "미안합니다 (Sorry)", "video_url": "mock_sorry.mp4"},
]


@app.route('/')
def index():
    return render_template('index.html')


# --- 1. 파일 업로드 API ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '선택된 파일이 없습니다.'}), 400

    file_id = str(uuid.uuid4())
    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}")
    file.save(save_path)

    return jsonify({'success': True, 'file_id': file_id, 'filename': filename})


# --- 2. 번역 작업 시작 API ---
@app.route('/api/translate', methods=['POST'])
def start_translate():
    data = request.json
    if not data or 'file_id' not in data:
        return jsonify({'success': False, 'error': '잘못된 요청입니다.'}), 400
    task_id = f"task_{str(uuid.uuid4())[:8]}"
    return jsonify({'success': True, 'task_id': task_id})


# --- 3. 진행 상황 스트리밍 (SSE) ---
# 이 부분도 예시를 위해 넣어논거 차후 수정이 필요함!!!!!!
@app.route('/api/translate/progress/<task_id>')
def stream_progress(task_id):
    def generate():
        steps = [
            (10, "동영상 로드 및 검증 중..."),
            (30, "프레임 추출 중..."),
            (50, "키포인트(관절) 추출 중..."),
            (70, "수어 인식 AI 모델 분석 중..."),
            (90, "결과 영상 렌더링 중..."),
        ]
        for progress, msg in steps:
            time.sleep(0.5)
            data = json.dumps({'progress': progress, 'message': msg})
            yield f"event: progress\ndata: {data}\n\n"

        time.sleep(0.5)
        # 완료 데이터 전송
        complete_data = json.dumps({
            'word': '안녕하세요 (Hello)',
            'task_id': task_id
        })
        yield f"event: complete\ndata: {complete_data}\n\n"

    return Response(generate(), mimetype='text/event-stream')


# --- 4. 단어 검색 API ---
@app.route('/api/search', methods=['POST'])
def search_dictionary():
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'success': True, 'results': []})

    # 부분 일치 검색 (대소문자 무시)
    results = [
        item for item in MOCK_DICTIONARY
        if query.lower() in item['word'].lower()
    ]
    return jsonify({'success': True, 'results': results})


# --- 5. 비디오 URL 제공 (Mock) ---
@app.route('/api/video/<video_type>/<id>')
def get_video_url(video_type, id):
    return jsonify({
        'url': f"/static/videos/{video_type}_{id}.mp4",
        'type': video_type
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)