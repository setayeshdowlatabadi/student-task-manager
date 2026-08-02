from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Task, SubTask
from .forms import TaskForm, RegisterForm

from django.shortcuts import render

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# ------------------------------------------------------------------
# ۱. احراز هویت (ثبت‌نام، ورود، خروج) با Toast Messages
# ------------------------------------------------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            
            # 🟢 اعتبارسنجی امنیت رمز عبور با قوانین settings.py
            try:
                validate_password(password)
            except ValidationError as e:
                # افزودن خطاهای رمز عبور به فرم
                for error in e.messages:
                    form.add_error('password', error)
                return render(request, 'tasks/register.html', {'form': form})

            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            login(request, user)
            messages.success(request, 'حساب کاربری شما با موفقیت ساخته شد. خوش آمدید!')
            return redirect('task_list')
        else:
            messages.error(request, 'خطایی در ثبت‌نام رخ داد. لطفاً ورودی‌ها را بررسی کنید.')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'خوش آمدید، {user.username}!')
            return redirect('task_list')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'با موفقیت از حساب کاربری خود خارج شدید.')
    return redirect('login')


# ------------------------------------------------------------------
# ۲. لیست تسک‌ها + آمار داشبورد + فیلتر و جستجو
# ------------------------------------------------------------------
@login_required
def task_list(request):
    # گرفتن تمام تسک‌های فعال کاربر با Custom Manager
    base_queryset = Task.objects.for_user(request.user)
    tasks = base_queryset

    # پارامترهای فیلتر و جستجو
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    # اعمال جستجو
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # اعمال فیلتر وضعیت
    if status_filter == 'completed':
        tasks = tasks.completed()
    elif status_filter == 'pending':
        tasks = tasks.pending()
    elif status_filter == 'today':
        tasks = tasks.today()
    elif status_filter == 'overdue':
        tasks = tasks.overdue()

    # اعمال فیلتر اولویت
    if priority_filter in ['HIGH', 'MEDIUM', 'LOW']:
        tasks = tasks.filter(priority=priority_filter)

    # مرتب‌سازی
    tasks = tasks.order_by('completed', 'deadline', '-created_at')

    # --- 📊 آمار کلیدی جهت نمایش در داشبورد ---
    total_count = base_queryset.count()
    completed_count = base_queryset.completed().count()
    pending_count = base_queryset.pending().count()
    overdue_count = base_queryset.overdue().count()
    today_count = base_queryset.today().count()

    # محاسبه درصد پیشرفت کل
    progress_percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0

    context = {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        # متغیرهای آماری داشبورد
        'total_count': total_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
        'today_count': today_count,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'tasks/task_list.html', context)


# ------------------------------------------------------------------
# ۳. مدیریت تسک‌ها (ایجاد، ویرایش، حذف نرم)
# ------------------------------------------------------------------
@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'تسک جدید با موفقیت ایجاد شد.')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'افزودن تسک جدید'})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_deleted=False)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'تسک با موفقیت به‌روزرسانی شد.')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'ویرایش تسک'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_deleted=False)
    if request.method == 'POST':
        # Soft Delete به جای حذف فیزیکی از دیتابیس
        task.is_deleted = True
        task.save()
        messages.success(request, 'تسک با موفقیت حذف شد.')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


# ------------------------------------------------------------------
# ۴. متدهای AJAX و تایمر پومودورو
# ------------------------------------------------------------------
@login_required
def toggle_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk, task__user=request.user, task__is_deleted=False)
    subtask.completed = not subtask.completed
    subtask.save()

    # پاسخ AJAX در صورت ارسال درخواست Fetch از فرانت‌اند
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'subtask_id': subtask.id,
            'completed': subtask.completed,
            'task_progress': subtask.task.subtask_progress_percentage
        })

    return redirect('task_list')


@login_required
@require_POST
def add_pomodoro_time(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_deleted=False)
    task.time_spent += 25
    task.save()
    return JsonResponse({
        'status': 'success',
        'new_time_spent': task.time_spent,
        'formatted_time': task.formatted_time_spent
    })

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def test_404(request):
    return render(request, '404.html', status=404)