from django.contrib import admin
from .models import Task, SubTask

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # ستون‌هایی که در لیست ادمین نمایش داده می‌شوند
    list_display = ('title', 'user', 'priority', 'completed', 'deadline', 'is_deleted', 'created_at')
    
    # فیلترهای سمت راست پنل ادمین
    list_filter = ('completed', 'priority', 'is_deleted', 'created_at')
    
    # قابلیت جستجو در عنوان، توضیحات و نام‌کاربری
    search_fields = ('title', 'description', 'user__username')
    
    # امکان تغییر سریع وضعیت تکمیل یا حذف از همان لیست
    list_editable = ('completed', 'is_deleted')
    
    # مدیریت زیرتسک‌ها درون صفحه خودِ تسک
    inlines = [SubTaskInline]