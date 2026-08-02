from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ۱. پنل ادمین
    path('admin/', admin.site.urls),
    
    # ۲. آدرس‌های اصلی اپلیکیشن تسک‌ها
    path('', include('tasks.urls')),
    
    # ۳. آدرس‌های فراموشی رمز عبور
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"), name="password_reset_sent"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_done_complete.html"), name="password_reset_complete"),
]

# 🚨 تنظیم هندلر صفحه 404
# نیازی به تغییر views.py نیست؛ Django به‌صورت خودکار تمپلیت templates/404.html را رندر می‌کند.
handler404 = 'django.views.defaults.page_not_found'