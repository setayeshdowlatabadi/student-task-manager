from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ------------------------------------------------------------------
# ۱. Custom QuerySet & Manager برای تمیزتر شدن کدهای views.py
# ------------------------------------------------------------------
class TaskQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user, is_deleted=False)

    def completed(self):
        return self.filter(completed=True)

    def pending(self):
        return self.filter(completed=False)

    def overdue(self):
        return self.filter(completed=False, deadline__lt=timezone.now())

    def today(self):
        today = timezone.now().date()
        return self.filter(deadline__date=today)


class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)


# ------------------------------------------------------------------
# ۲. مدل اصلی تسک (تکمیل شده و بدون تکرار)
# ------------------------------------------------------------------
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'کم'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'بالا'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    # ⏱️ فیلدهای ثبت زمان (بر حسب دقیقه)
    estimated_time = models.PositiveIntegerField(default=0, help_text="زمان تخمینی به دقیقه")
    time_spent = models.PositiveIntegerField(default=0, help_text="زمان صرف شده به دقیقه")
    
    # 🗑️ قابلیت Soft Delete (برای جلوگیری از حذف فیزیکی ناگهانی)
    is_deleted = models.BooleanField(default=False)

    objects = TaskManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    # متد کمکی: آیا مهلت انجام گذشته است؟
    @property
    def is_overdue(self):
        if self.deadline and not self.completed:
            return timezone.now() > self.deadline
        return False

    # متد کمکی: فرمت نمایش زمان صرف‌شده به ساعت و دقیقه
    @property
    def formatted_time_spent(self):
        hours = self.time_spent // 60
        minutes = self.time_spent % 60
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"

    # 📊 متد کمکی جدید: محاسبه درصد پیشرفت SubTaskهای این تسک
    @property
    def subtask_progress_percentage(self):
        total_subtasks = self.subtasks.count()
        if total_subtasks == 0:
            return 100 if self.completed else 0
        completed_subtasks = self.subtasks.filter(completed=True).count()
        return int((completed_subtasks / total_subtasks) * 100)


# ------------------------------------------------------------------
# ۳. مدل زیرتسک (چک‌لیست)
# ------------------------------------------------------------------
class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# ------------------------------------------------------------------
# ۴. مدل فایل پیوست
# ------------------------------------------------------------------
class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]