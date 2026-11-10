import io
import csv
from flask import Flask, jsonify, request, render_template_string, url_for, abort, redirect, make_response

app = Flask(__name__)

# Dữ liệu sinh viên mẫu
STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def tinh_diem_tb_va_xep_loai(scores):
    if not scores:
        return "-", "-"
    dtb = round(sum(scores.values()) / len(scores), 2)
    if dtb >= 8.5:
        xep_loai = "Giỏi"
    elif dtb >= 7.0:
        xep_loai = "Khá"
    elif dtb >= 5.0:
        xep_loai = "Trung bình"
    else:
        xep_loai = "Yếu"
    return dtb, xep_loai

def lay_danh_sach_lop():
    return sorted(list({info["lop"] for info in STUDENTS.values()}))


# --- CÂU 1: Trang chủ / ---
@app.route('/')
def home():
    tong_sv = len(STUDENTS)
    ds_lop = lay_danh_sach_lop()
    tong_so_lop = len(ds_lop)
    
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Trang chủ - Quản lý sinh viên</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container my-5">
            <div class="card shadow-sm mx-auto" style="max-width: 600px;">
                <div class="card-body p-4">
                    <h1 class="card-title text-primary mb-4 text-center">Trang Chủ</h1>
                    
                    <!-- Ô tìm kiếm nhanh ở trang chủ -->
                    <form action="{{ url_for('search_students') }}" method="GET" class="mb-4">
                        <div class="input-group">
                            <input type="text" name="q" class="form-control" placeholder="Nhập tên hoặc MSSV để tìm kiếm...">
                            <button class="btn btn-primary" type="submit">Tìm kiếm</button>
                        </div>
                    </form>

                    <div class="list-group mb-4">
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            Tổng số sinh viên
                            <span class="badge bg-primary rounded-pill">{{ tong_sv }}</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            Số lớp (không trùng)
                            <span class="badge bg-success rounded-pill">{{ tong_so_lop }}</span>
                        </div>
                    </div>

                    <div class="d-grid gap-2">
                        <a href="{{ url_for('students_list') }}" class="btn btn-outline-primary">
                            Xem danh sách sinh viên (/students)
                        </a>
                        <a href="{{ url_for('students_api') }}" class="btn btn-outline-secondary" target="_blank">
                            Xem dữ liệu API (/api/students)
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, tong_sv=tong_sv, tong_so_lop=tong_so_lop)


# --- CÂU 1: API /api/students ---
@app.route('/api/students', endpoint='students_api')
def get_students_api():
    ds_lop = lay_danh_sach_lop()
    return jsonify({
        "tong_so_sinh_vien": len(STUDENTS),
        "tong_so_lop": len(ds_lop),
        "danh_sach_lop": ds_lop,
        "data": STUDENTS
    })


# --- CÂU 2: Route /students ---
@app.route('/students', endpoint='students_list')
def show_students():
    lop_filter = request.args.get('Lop', '').strip()
    danh_sach_lop = lay_danh_sach_lop()
    
    danh_sach_hien_thi = []
    for mssv, info in STUDENTS.items():
        if lop_filter and info['lop'].lower() != lop_filter.lower():
            continue
            
        dtb, xep_loai = tinh_diem_tb_va_xep_loai(info['scores'])
        danh_sach_hien_thi.append({
            'mssv': mssv,
            'name': info['name'],
            'lop': info['lop'],
            'dtb': dtb,
            'xep_loai': xep_loai
        })
        
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Danh sách sinh viên</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container my-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-primary mb-0">Danh sách sinh viên</h2>
                <div>
                    <a href="{{ url_for('search_students') }}" class="btn btn-outline-primary btn-sm me-2">🔍 Trang tìm kiếm</a>
                    <a href="/" class="btn btn-sm btn-secondary">Quay lại Trang chủ</a>
                </div>
            </div>

            <div class="card p-3 mb-4 shadow-sm">
                <div class="d-flex align-items-center">
                    <span class="fw-bold me-3">Lọc theo lớp:</span>
                    <div class="btn-group" role="group">
                        <a href="{{ url_for('students_list') }}" 
                           class="btn btn-outline-primary {{ 'active' if not current_lop else '' }}">
                            Tất cả
                        </a>
                        {% for lop in danh_sach_lop %}
                            <a href="{{ url_for('students_list', Lop=lop) }}" 
                               class="btn btn-outline-primary {{ 'active' if current_lop.lower() == lop.lower() else '' }}">
                                {{ lop }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
            </div>

            {% if danh_sach_hien_thi %}
            <div class="table-responsive card shadow-sm">
                <table class="table table-hover table-striped mb-0 align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>MSSV</th>
                            <th>Họ tên</th>
                            <th>Lớp</th>
                            <th>Điểm TB</th>
                            <th>Xếp loại</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sv in danh_sach_hien_thi %}
                        <tr>
                            <td>
                                <a href="{{ url_for('student_detail', mssv=sv.mssv) }}" class="fw-bold text-decoration-none">
                                    {{ sv.mssv }}
                                </a>
                            </td>
                            <td>{{ sv.name }}</td>
                            <td><span class="badge bg-info text-dark">{{ sv.lop }}</span></td>
                            <td>{{ sv.dtb }}</td>
                            <td>
                                {% if sv.xep_loai == 'Giỏi' %}
                                    <span class="badge bg-success">Giỏi</span>
                                {% elif sv.xep_loai == 'Khá' %}
                                    <span class="badge bg-primary">Khá</span>
                                {% elif sv.xep_loai == 'Trung bình' %}
                                    <span class="badge bg-warning text-dark">Trung bình</span>
                                {% elif sv.xep_loai == 'Yếu' %}
                                    <span class="badge bg-danger">Yếu</span>
                                {% else %}
                                    <span class="badge bg-secondary">-</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="alert alert-warning text-center shadow-sm" role="alert">
                Không có sinh viên phù hợp.
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html, 
        danh_sach_hien_thi=danh_sach_hien_thi, 
        danh_sach_lop=danh_sach_lop, 
        current_lop=lop_filter
    )


# --- CÂU 3: Route chi tiết /students/<mssv> ---
@app.route('/students/<mssv>', endpoint='student_detail')
def get_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    sv = STUDENTS[mssv]
    dtb, xep_loai = tinh_diem_tb_va_xep_loai(sv['scores'])
    short_link = url_for('redirect_student', mssv=mssv, _external=True)
    
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Chi tiết sinh viên - {{ mssv }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container my-5" style="max-width: 700px;">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h2 class="text-primary mb-0">Thông tin chi tiết sinh viên</h2>
                <a href="{{ url_for('students_list') }}" class="btn btn-outline-secondary btn-sm">Quay lại danh sách</a>
            </div>

            <div class="card shadow-sm mb-4">
                <div class="card-body">
                    <p class="mb-2"><strong>MSSV:</strong> {{ mssv }}</p>
                    <p class="mb-2"><strong>Họ tên:</strong> {{ sv.name }}</p>
                    <p class="mb-2"><strong>Lớp:</strong> 
                        <a href="{{ url_for('students_list', Lop=sv.lop) }}" class="badge bg-info text-dark text-decoration-none">
                            {{ sv.lop }}
                        </a>
                    </p>
                    <p class="mb-2"><strong>Điểm TB:</strong> {{ dtb }}</p>
                    <p class="mb-2"><strong>Xếp loại:</strong> {{ xep_loai }}</p>
                    <p class="mb-0"><strong>Link rút gọn:</strong> <a href="{{ short_link }}" target="_blank">{{ short_link }}</a></p>
                </div>
                <div class="card-footer bg-white border-top-0 pt-0 pb-3">
                    <a href="{{ url_for('export_student_csv', mssv=mssv) }}" class="btn btn-success btn-sm">
                        📥 Tải bảng điểm (CSV)
                    </a>
                </div>
            </div>

            <h4 class="text-secondary mb-3">Bảng điểm từng học phần</h4>
            {% if sv.scores %}
            <div class="card shadow-sm">
                <table class="table table-bordered mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Mã học phần</th>
                            <th>Điểm số</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for mon, diem in sv.scores.items() %}
                        <tr>
                            <td>{{ mon }}</td>
                            <td>{{ diem }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="alert alert-secondary" role="alert">
                Sinh viên chưa có điểm học phần nào.
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, mssv=mssv, sv=sv, dtb=dtb, xep_loai=xep_loai, short_link=short_link)


# --- CÂU 4: Link rút gọn /sv/<mssv> chuyển hướng 301 ---
@app.route('/sv/<mssv>', endpoint='redirect_student')
def redirect_student(mssv):
    return redirect(url_for('student_detail', mssv=mssv), code=301)


# --- CÂU 5: Xuất bảng điểm CSV /students/<mssv>/export ---
@app.route('/students/<mssv>/export', endpoint='export_student_csv')
def export_student_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    scores = STUDENTS[mssv]['scores']
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['hoc_phan', 'diem'])
    
    for mon, diem in scores.items():
        writer.writerow([mon, diem])
        
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    
    return response


# --- CÂU 6: Tìm kiếm an toàn (Chống XSS) /search?q=... ---
@app.route('/search', endpoint='search_students')
def search_students():
    # Lấy từ khóa từ tham số query 'q'
    keyword = request.args.get('q', '')
    
    danh_sach_ket_qua = []
    
    if keyword:
        kw_lower = keyword.lower()
        for mssv, info in STUDENTS.items():
            # Tìm sinh viên có họ tên HOẶC MSSV chứa từ khóa (không phân biệt hoa thường)
            if kw_lower in info['name'].lower() or kw_lower in mssv.lower():
                dtb, xep_loai = tinh_diem_tb_va_xep_loai(info['scores'])
                danh_sach_ket_qua.append({
                    'mssv': mssv,
                    'name': info['name'],
                    'lop': info['lop'],
                    'dtb': dtb,
                    'xep_loai': xep_loai
                })

    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Tìm kiếm sinh viên</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container my-5" style="max-width: 800px;">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-primary mb-0">Tìm kiếm sinh viên</h2>
                <a href="{{ url_for('students_list') }}" class="btn btn-outline-secondary btn-sm">Xem tất cả danh sách</a>
            </div>

            <!-- Form GET chứa ô nhập, giữ lại từ khóa đã nhập qua thuộc tính value -->
            <div class="card p-4 shadow-sm mb-4">
                <form action="{{ url_for('search_students') }}" method="GET">
                    <div class="input-group">
                        <input type="text" name="q" class="form-control" 
                               placeholder="Nhập tên hoặc MSSV..." 
                               value="{{ keyword }}">
                        <button class="btn btn-primary" type="submit">Tìm kiếm</button>
                    </div>
                </form>
            </div>

            <!-- Xuất hiện từ khóa ở phần kết quả (được tự động escape chống XSS) -->
            {% if keyword %}
                <h5 class="mb-3">Tìm thấy {{ danh_sach_ket_qua|length }} kết quả cho "<strong>{{ keyword }}</strong>":</h5>

                {% if danh_sach_ket_qua %}
                <div class="card shadow-sm">
                    <div class="list-group list-group-flush">
                        {% for sv in danh_sach_ket_qua %}
                        <a href="{{ url_for('student_detail', mssv=sv.mssv) }}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{{ sv.name }}</strong> (MSSV: {{ sv.mssv }})
                                <br>
                                <small class="text-muted">Lớp: {{ sv.lop }} | Điểm TB: {{ sv.dtb }} | Xếp loại: {{ sv.xep_loai }}</small>
                            </div>
                            <span class="btn btn-sm btn-outline-primary">Xem chi tiết</span>
                        </a>
                        {% endfor %}
                    </div>
                </div>
                {% else %}
                <div class="alert alert-warning shadow-sm" role="alert">
                    Không tìm thấy sinh viên nào phù hợp.
                </div>
                {% endif %}
            {% endif %}
        </div>
    </body>
    </html>
    """
    
    # Jinja2 tự động escape giá trị 'keyword' chống tấn công XSS
    return render_template_string(html, keyword=keyword, danh_sach_ket_qua=danh_sach_ket_qua)


if __name__ == '__main__':
    app.run(debug=True)