document.addEventListener('DOMContentLoaded', async function() {
    try {
        const userResponse = await fetch('/api/user');
        if (!userResponse.ok) {
            window.location.href = '/login';
            return;
        }
        const user = await userResponse.json();
        document.getElementById('username').textContent = user.username;
        
        document.getElementById('logoutBtn').addEventListener('click', async function() {
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = '/login';
        });
        
        document.getElementById('passwordForm').addEventListener('submit', changePassword);
    } catch (err) {
        window.location.href = '/login';
    }
});

async function changePassword(e) {
    e.preventDefault();
    
    const oldPassword = document.getElementById('old_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (newPassword !== confirmPassword) {
        showError('Новые пароли не совпадают');
        return;
    }
    
    const formData = new URLSearchParams();
    formData.append('old_password', oldPassword);
    formData.append('new_password', newPassword);
    formData.append('confirm_password', confirmPassword);
    
    try {
        const response = await fetch('/api/profile/change-password', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            showSuccess('Пароль успешно изменен');
            document.getElementById('passwordForm').reset();
        } else {
            showError(data.error);
        }
    } catch (err) {
        showError('Ошибка соединения');
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    const successDiv = document.getElementById('success');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    successDiv.style.display = 'none';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('success');
    const errorDiv = document.getElementById('error');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}