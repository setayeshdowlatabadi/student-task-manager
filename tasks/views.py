from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Task, SubTask
from .forms import TaskForm, RegisterForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# ۱. ثبت‌نام کاربر جدید
def register_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('task_list')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

# ۲. ورود کاربر
def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})

# ۳. خروج کاربر
def logout_view(request):
    logout(request)
    return redirect('login')

# ۴. مشاهده لیست تسک‌ها + امکان جستجو و فیلتر
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # دریافت پارامترهای فیلتر
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    # فیلتر جستجو
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    # فیلتر وضعیت (تکمیل شده / نشده)
    if status_filter == 'completed':
        tasks = tasks.filter(completed=True)
    elif status_filter == 'pending':
        tasks = tasks.filter(completed=False)

    # فیلتر سطح اولویت
    if priority_filter in ['HIGH', 'MEDIUM', 'LOW']:
        tasks = tasks.filter(priority=priority_filter)

    # مرتب‌سازی بر اساس وضعیت، مهلت انجام و زمان ساخت
    tasks = tasks.order_by('completed', 'deadline', '-created_at')

    context = {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'tasks/task_list.html', context)

# ۵. ثبت تسک جدید
@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'افزودن تسک جدید'})

# ۶. ویرایش تسک
@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'ویرایش تسک'})

# ۷. حذف تسک
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

# ۸. تغییر وضعیت زیرتسک
@login_required
def toggle_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk, task__user=request.user)
    subtask.completed = not subtask.completed
    subtask.save()
    return redirect('task_list')

@login_required
@require_POST
def add_pomodoro_time(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    # اضافه کردن ۲۵ دقیقه به زمان صرف‌شده
    task.time_spent += 25
    task.save()
    return JsonResponse({
        'status': 'success',
        'new_time_spent': task.time_spent,
        'formatted_time': task.formatted_time_spent
    })