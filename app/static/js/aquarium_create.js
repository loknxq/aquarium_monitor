let aquariumId = null;

document.addEventListener('DOMContentLoaded', async function() {
    try {
        const userResponse = await fetch('/api/user');
        if (!userResponse.ok) {
            window.location.href = '/login';
            return;
        }
        
        await loadParameters();
        
        document.getElementById('photo_input').addEventListener('change', handlePhotoUpload);
        document.getElementById('createForm').addEventListener('submit', createAquarium);
    } catch (err) {
        window.location.href = '/login';
    }
});

async function loadParameters() {
    const response = await fetch('/api/parameters');
    const parameters = await response.json();
    const container = document.getElementById('parameters_checkboxes');
    
    container.innerHTML = parameters.map(p => `
        <label class="checkbox-item">
            <input type="checkbox" value="${p.id}" class="param-checkbox"> ${p.display_name} (${p.unit})
        </label>
    `).join('');
}

function handlePhotoUpload(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const maxWidth = 300;
                const scale = maxWidth / img.width;
                canvas.width = maxWidth;
                canvas.height = img.height * scale;
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                document.getElementById('photo_base64').value = canvas.toDataURL('image/jpeg', 0.7);
                const preview = document.getElementById('photo_preview');
                preview.src = canvas.toDataURL('image/jpeg', 0.7);
                preview.style.display = 'block';
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
}

async function createAquarium(e) {
    e.preventDefault();
    
    const selectedParams = Array.from(document.querySelectorAll('.param-checkbox:checked')).map(cb => parseInt(cb.value));
    if (selectedParams.length === 0) {
        showError('Выберите хотя бы один параметр');
        return;
    }
    
    const formData = new URLSearchParams();
    formData.append('name', document.getElementById('name').value);
    formData.append('inhabitants', document.getElementById('inhabitants').value);
    formData.append('photo', document.getElementById('photo_base64').value);
    selectedParams.forEach(p => formData.append('parameters', p));
    
    try {
        const response = await fetch('/api/aquariums', {
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
        showError('Ошибка при создании аквариума');
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}