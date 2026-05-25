document.addEventListener('DOMContentLoaded', async function() {
    try {
        const userResponse = await fetch('/api/user');
        if (!userResponse.ok) {
            window.location.href = '/login';
            return;
        }
        const user = await userResponse.json();
        document.getElementById('username').textContent = user.username;
        
        await loadAquariums();
        
        document.getElementById('logoutBtn').addEventListener('click', async function() {
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = '/login';
        });
    } catch (err) {
        window.location.href = '/login';
    }
});

async function loadAquariums() {
    const response = await fetch('/api/aquariums');
    const aquariums = await response.json();
    const grid = document.getElementById('aquariumsGrid');
    
    if (aquariums.length === 0) {
        grid.innerHTML = '<div class="card"><p>У вас пока нет аквариумов. Создайте первый!</p></div>';
        return;
    }
    
    grid.innerHTML = aquariums.map(a => `
        <div class="aquarium-card">
            <button class="delete-btn" onclick="deleteAquarium(${a.id})">×</button>
            <a href="/aquarium/${a.id}">
                ${a.photo ? `<img src="${a.photo}" style="width:100%; height:150px; object-fit:cover; border-radius:8px; margin-bottom:10px;">` : ''}
                <h3>${escapeHtml(a.name)}</h3>
                <p>Создан: ${new Date(a.created_at).toLocaleDateString()}</p>
            </a>
        </div>
    `).join('');
}

window.deleteAquarium = async function(id) {
    if (confirm('Удалить аквариум? Все данные будут потеряны.')) {
        await fetch(`/api/aquariums/${id}`, { method: 'DELETE' });
        await loadAquariums();
    }
};

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}