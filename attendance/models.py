from django.db import models

class Employee(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # ←これだけ残す

    def __str__(self):
        return self.name

    def calculate_salary(self, year, month, hourly_wage=1000):
        from .models import Attendance  # 循環インポート防止
        records = Attendance.objects.filter(
            employee=self,
            date__year=year,
            date__month=month
        )

        total_seconds = 0
        for record in records:
            if record.clock_in and record.clock_out:
                duration = (record.clock_out - record.clock_in).total_seconds()

                # 労働時間に応じた休憩時間を控除
                hours = duration / 3600
                if hours > 8:
                    duration -= 3600  # 1時間の休憩
                elif hours > 6:
                    duration -= 45 * 60  # 45分の休憩
                # 6時間以下は休憩なし

                total_seconds += max(duration, 0)  # マイナスにならないように

        total_hours = total_seconds / 3600
        return round(total_hours * hourly_wage, 2)



class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.date}"
    @property
    def working_hours(self):
        if self.clock_in and self.clock_out:
            total_seconds = (self.clock_out - self.clock_in).total_seconds()
            hours = total_seconds / 3600

            # 日本の労働基準法に基づく休憩時間控除
            if hours > 8:
                total_seconds -= 3600  # 1時間休憩
            elif hours > 6:
                total_seconds -= 45 * 60  # 45分休憩

            return round(total_seconds / 3600, 2)
        return 0
