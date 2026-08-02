from django import forms
from django.contrib.auth.models import User
from .models import Task

class TaskForm(forms.ModelForm):
    # تنظیم دیت‌پیکر برای فیلد Deadline
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='مهلت انجام (Deadline)'
    )

    class Meta:
        model = Task
        # فیلد priority به لیست اضافه شد
        fields = ['title', 'description', 'priority', 'completed', 'deadline', 'estimated_time', 'time_spent']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان تسک...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیحات تکمیلی...'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estimated_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً ۶۰ (به دقیقه)'}),
            'time_spent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً ۴۵ (به دقیقه)'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'عنوان',
            'description': 'توضیحات',
            'priority': 'سطح اولویت',
            'completed': 'انجام شده',
        }

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='کلمه عبور')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='تکرار کلمه عبور')

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("کلمه‌های عبور وارد شده یکسان نیستند.")
        return cleaned_data