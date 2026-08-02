from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'کم'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'زیاد'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    # متد کمکی برای بررسی گذشته بودن مهلت
    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.deadline and not self.completed:
            return timezone.now() > self.deadline
        return False

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'کم'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'بالا'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # ⏱️ فیلدهای جدید ثبت زمان (بر حسب دقیقه)
    estimated_time = models.PositiveIntegerField(default=0, help_text="زمان تخمینی به دقیقه")
    time_spent = models.PositiveIntegerField(default=0, help_text="زمان صرف شده به دقیقه")

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.deadline and not self.completed:
            return timezone.now() > self.deadline
        return False
        
    # متد کمکی برای تبدیل دقیقه به فرمت ساعت و دقیقه
    @property
    def formatted_time_spent(self):
        hours = self.time_spent // 60
        minutes = self.time_spent % 60
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"
    
    
# مدل زیرتسک (چک‌لیست)
class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# مدل فایل پیوست
class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]