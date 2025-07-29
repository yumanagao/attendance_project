from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 従業員のQRコード表示ページ
    path('show_qr/<str:employee_id>/', views.show_employee_qr, name='show_employee_qr'),

    # 従業員作成ページ（フォーム）
    path('create_employee/', views.create_employee, name='create_employee'),  # 従業員作成ページ

    # 従業員一覧ページ
    path('employee_list/', views.employee_list, name='employee_list'),  # 従業員一覧ページ

    # 勤怠打刻ページ
    path('clock_in_out/', views.clock_in_out, name='clock_in_out'),  # 出退勤打刻ページ

    # 出退勤打刻用のページ
    path('clock_in_out_page/', views.clock_in_out_page, name='clock_in_out_page'),

    path('attendance_history/', views.attendance_history, name='attendance_history'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('attendance/edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('', views.home, name='home'),
    path('admin_home/', views.admin_home, name='admin_home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)