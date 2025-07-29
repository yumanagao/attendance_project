import qrcode
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from cryptography.fernet import Fernet
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Attendance, Employee
from .forms import EmployeeForm
import pandas as pd
import json
import os
from django import forms
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods


# --- 🔐 秘密鍵の読み込み（settings.py に保存したキーを使用） ---
SECRET_QR_KEY = getattr(settings, "QR_SECRET_KEY", None)
if SECRET_QR_KEY is None:
    raise Exception("QR_SECRET_KEY が settings.py に設定されていません。")
cipher_suite = Fernet(SECRET_QR_KEY)
def is_admin(user):
    return user.is_authenticated and user.is_staff

# 🔧 QRコード画像生成関数
@user_passes_test(is_admin, login_url='admin_login')
def generate_qr_image(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())

# 🕒 出退勤記録（QRスキャン時に呼ばれる）
@csrf_exempt
def clock_in_out(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            today = timezone.localdate()

            decrypted_data = cipher_suite.decrypt(qr_data.encode()).decode()
            user_id, name = decrypted_data.split(',')

            employee = Employee.objects.get(user_id=user_id)
            attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

            if created or not attendance.clock_in:
                attendance.clock_in = timezone.now()
                message_type = "clock_in"
                greeting = f"{employee.name} さん、おはようございます。出勤打刻が完了しました。"
            else:
                attendance.clock_out = timezone.now()
                message_type = "clock_out"
                greeting = f"{employee.name} さん、お疲れ様でした。退勤打刻が完了しました。"

            attendance.save()
            return JsonResponse({
                'status': 'success',
                'message': greeting,
                'message_type': message_type
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'エラーが発生しました: {str(e)}'
            })

    return JsonResponse({'status': 'error', 'message': '無効なリクエスト'})

# 📋 打刻ページ（テンプレートでカメラ起動）
def clock_in_out_page(request):
    return render(request, 'attendance/clock_in_out.html')

# 👤 従業員作成（QRコードも同時生成）
@user_passes_test(is_admin, login_url='admin_login')
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()

            # --- QRコードを自動生成して保存 ---
            encrypted_data = cipher_suite.encrypt(f"{employee.user_id},{employee.name}".encode())

            qr_image_content = generate_qr_image(encrypted_data)

            # ✅ ファイル名を定義
            filename = f"{employee.user_id}_qr.png"

            # ✅ 保存処理
            employee.qr_image.save(filename, qr_image_content)
            employee.save()

            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'attendance/create_employee.html', {'form': form})

# 👥 従業員一覧
@user_passes_test(is_admin, login_url='admin_login')
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'attendance/employee_list.html', {'employees': employees})

# 🎟 従業員QRコード表示
@user_passes_test(is_admin, login_url='admin_login')
def show_employee_qr(request, employee_id):
    try:
        employee = Employee.objects.get(user_id=employee_id)  # 主キーでなく user_id に修正
        return render(request, 'attendance/show_qr.html', {'employee': employee})
    except Employee.DoesNotExist:
        return HttpResponse("従業員が見つかりません。", status=404)

@user_passes_test(is_admin, login_url='admin_login')
def attendance_history(request):
    records = Attendance.objects.select_related('employee').order_by('-date')
    return render(request, 'attendance/attendance_history.html', {'records': records})

class MonthYearForm(forms.Form):
    year = forms.IntegerField(label='年', initial=timezone.localtime().year)
    month = forms.IntegerField(label='月', initial=timezone.localtime().month)



@user_passes_test(is_admin, login_url='admin_login')
@login_required(login_url='admin_login')
def admin_dashboard(request):
    form = MonthYearForm(request.GET or None)

    # 年月の指定がある場合はその値を使う
    if form.is_valid():
        year = form.cleaned_data['year']
        month = form.cleaned_data['month']
    else:
        year = timezone.localtime().year
        month = timezone.localtime().month

    employees = Employee.objects.all()
    dashboard_data = []

    for emp in employees:
        salary = emp.calculate_salary(year, month)
        records = Attendance.objects.filter(employee=emp, date__year=year, date__month=month)
        dashboard_data.append({
            'employee': emp,
            'records': records,
            'salary': salary,
        })

    return render(request, 'attendance/admin_dashboard.html', {
        'form': form,
        'dashboard_data': dashboard_data,
        'year': year,
        'month': month,
    })

AttendanceForm = modelform_factory(Attendance, fields=['clock_in', 'clock_out'])
def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'attendance/edit_attendance.html', {'form': form, 'attendance': attendance})


def admin_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_home')
        else:
            messages.error(request, "ログインに失敗しました")
    return render(request, "attendance/admin_login.html")


def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def home(request):
    return render(request, 'attendance/home.html')

@user_passes_test(is_admin, login_url='admin_login')
@login_required(login_url='admin_login')
def admin_home(request):
    return render(request, 'attendance/admin_home.html')

