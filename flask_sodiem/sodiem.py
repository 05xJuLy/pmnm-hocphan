STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "Lop": "K47A", "scores": {"PMMN": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "Lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "Lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "Lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "Lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "Lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

from flask import Flask, url_for, request, jsonify, abort, redirect, make_response, render_template

app = Flask(__name__)
app.json.ensure_ascii = False

def tinh_dtb_va_xep_loai(scores):
    if not scores:
        return "-", "Không có điểm"
    dtb = round(sum(scores.values()) / len(scores), 2)
    if dtb >= 9.0: xl = "Xuất sắc"
    elif dtb >= 8.0: xl = "Giỏi"
    elif dtb >= 6.5: xl = "Khá"
    elif dtb >= 5.0: xl = "Trung bình"
    else: xl = "Yếu"
    return dtb, xl

@app.route("/")
def trangchu():
    tong_sv = len(STUDENTS)
    classes = sorted(set(sv["Lop"] for sv in STUDENTS.values())) # sắp xếp những tên lớp không trùng lặp
    return render_template("index.html", tong_sv=tong_sv, cac_lop=len(classes), danh_sach_lop=classes)

@app.route("/students")
def students():
    selected_lop = request.args.get("lop", "").strip().lower() # lấy tham số lớp trên URL
    cac_lop_set = sorted(set(sv["Lop"] for sv in STUDENTS.values())) # lấy ds các lớp
    danh_sach_hien_thi = []
    for masv, info in STUDENTS.items():
        if not selected_lop or info["Lop"].lower() == selected_lop:
            dtb, xep_loai = tinh_dtb_va_xep_loai(info["scores"])
            danh_sach_hien_thi.append({
                "masv": masv,
                "name": info["name"],
                "lop": info["Lop"],
                "dtb": dtb,
                "xep_loai": xep_loai
            })
    return render_template("students.html", 
                           students=danh_sach_hien_thi, 
                           classes=cac_lop_set, 
                           selected_lop=selected_lop.upper())

@app.route("/students/<mssv>")
def student_detail(mssv): 
    if mssv not in STUDENTS: # kiểm tra mssv có tồn tại không nếu không thì in ra
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    
    sv = STUDENTS[mssv]
    dtb, xep_loai = tinh_dtb_va_xep_loai(sv["scores"])
    
    return render_template("detail.html", mssv=mssv, sv=sv, dtb=dtb, xep_loai=xep_loai)

@app.route("/sv/<mssv>") 
def short_student_detail(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301) 

@app.route("/students/<mssv>/export")
def export_student_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    sv = STUDENTS[mssv]
    lines = ["hoc_phan,diem"]
    for mon, diem in sv["scores"].items():
        lines.append(f"{mon},{diem}")
    csv_content = "\n".join(lines)
    
    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    
    return response

@app.route("/search")
def search():
    query = request.args.get("q", "").strip() 
    results = []
    if query:
        query_lower = query.lower()
        for mssv, info in STUDENTS.items():
            if query_lower in info["name"].lower() or query_lower in mssv.lower():
                dtb, xep_loai = tinh_dtb_va_xep_loai(info["scores"])
                results.append({
                    "masv": mssv,
                    "name": info["name"],
                    "lop": info["Lop"],
                    "dtb": dtb,
                    "xep_loai": xep_loai
                })

    return render_template("students.html", 
                           students=results, 
                           search_query=query, 
                           is_search=True)

@app.route("/api/students")
def api_students():
    return jsonify(STUDENTS)

if __name__ == "__main__":
    app.run(debug=True)
