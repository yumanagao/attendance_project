from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['user_id', 'name']  # 必要なフィールドを指定します
        labels = {
            'user_id': '従業員ID',
            'name': '名前',
        }
