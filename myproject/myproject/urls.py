"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from attendance import views as attendance_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('attendance/', include('attendance.urls')),
    path('admin_login/', auth_views.LoginView.as_view(template_name='attendance/admin_login.html'), name='admin_login'),
    path('admin_logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='admin_logout'),
    path('', attendance_views.home, name='home')
]

# 開発サーバでメディアファイルを扱うための設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)