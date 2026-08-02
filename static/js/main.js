// --- ۱. مدیریت تم دارک / لایت ---
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
});

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    
    const icon = document.getElementById('themeIcon');
    if (icon) {
        if (theme === 'dark') {
            icon.className = 'fa-solid fa-sun text-warning';
        } else {
            icon.className = 'fa-solid fa-moon text-secondary';
        }
    }
}

// --- ۲. مدیریت تایمر پومودورو (با استراحت و ثبت خودکار در دیتابیس) ---
const timerIntervals = {};
const timerSeconds = {};
const timerModes = {}; // وضعیت: 'work' (کاری) یا 'break' (استراحت)

function startTimer(taskId) {
    if (timerIntervals[taskId]) return; 

    // تنظیم حالت اولیه روی ۲۵ دقیقه کار
    if (timerSeconds[taskId] === undefined) {
        timerSeconds[taskId] = 25 * 60;
        timerModes[taskId] = 'work';
    }

    const display = document.getElementById(`timer-display-${taskId}`);

    timerIntervals[taskId] = setInterval(() => {
        if (timerSeconds[taskId] <= 0) {
            clearInterval(timerIntervals[taskId]);
            delete timerIntervals[taskId];

            if (timerModes[taskId] === 'work') {
                // ارسال درخواست به Django برای اضافه کردن ۲۵ دقیقه به دیتابیس
                fetch(`/task/${taskId}/add-pomodoro/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const spentElem = document.getElementById(`time-spent-${taskId}`);
                        if (spentElem) spentElem.innerText = data.formatted_time;
                    }
                });

                // سوئیچ به ۵ دقیقه استراحت
                timerModes[taskId] = 'break';
                timerSeconds[taskId] = 5 * 60;
                display.innerText = "05:00";

                Swal.fire({
                    title: 'پومودورو تمام شد! ☕',
                    text: '۲۵ دقیقه به زمان ثبت‌شده اضافه شد. ۵ دقیقه استراحت کنید!',
                    icon: 'success',
                    confirmButtonText: 'شروع استراحت'
                });

            } else {
                // سوئیچ مجدد به ۲۵ دقیقه کار
                timerModes[taskId] = 'work';
                timerSeconds[taskId] = 25 * 60;
                display.innerText = "25:00";

                Swal.fire({
                    title: 'استراحت تمام شد! 🚀',
                    text: 'آماده‌اید برای پومودورو ۲۵ دقیقه‌ای بعدی؟',
                    icon: 'info',
                    confirmButtonText: 'بزن بریم'
                });
            }
            return;
        }

        timerSeconds[taskId]--;

        let mins = Math.floor(timerSeconds[taskId] / 60);
        let secs = timerSeconds[taskId] % 60;
        display.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopTimer(taskId) {
    if (timerIntervals[taskId]) {
        clearInterval(timerIntervals[taskId]);
        delete timerIntervals[taskId];
    }
}

function resetTimer(taskId) {
    stopTimer(taskId);
    timerModes[taskId] = 'work';
    timerSeconds[taskId] = 25 * 60;
    const display = document.getElementById(`timer-display-${taskId}`);
    if (display) display.innerText = "25:00";
}

// تابع کمکی دریافت کوکی CSRF برای درخواست‌های AJAX در جنگو
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- ۳. پاپ‌آپ تأیید حذف با SweetAlert2 ---
function confirmDelete(event, formId) {
    event.preventDefault();
    Swal.fire({
        title: 'آیا از حذف این تسک اطمینان دارید؟',
        text: "این عملیات قابل بازگشت نیست!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'بله، حذف کن!',
        cancelButtonText: 'انصراف'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById(formId).submit();
        }
    });
}