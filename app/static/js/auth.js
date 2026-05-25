document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new URLSearchParams();
            formData.append('username', document.getElementById('username').value);
            formData.append('password', document.getElementById('password').value);
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error);
                }
            } catch (err) {
                showError('Ошибка соединения');
            }
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new URLSearchParams();
            formData.append('username', document.getElementById('username').value);
            formData.append('password', document.getElementById('password').value);
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error);
                }
            } catch (err) {
                showError('Ошибка соединения');
            }
        });
    }
});

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}