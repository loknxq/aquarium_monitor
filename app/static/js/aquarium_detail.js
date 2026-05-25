let aquariumId = null;
let currentChart = null;
let aquariumParams = [];

document.addEventListener('DOMContentLoaded', async function() {
    try {
        const userResponse = await fetch('/api/user');
        if (!userResponse.ok) {
            window.location.href = '/login';
            return;
        }
        
        aquariumId = window.location.pathname.split('/').pop();
        await loadAquariumData();
        await loadMeasurements();
        
        document.getElementById('measurement_date').value = new Date().toISOString().split('T')[0];
    } catch (err) {
        window.location.href = '/login';
    }
});

async function loadAquariumData() {
    const response = await fetch(`/api/aquariums/${aquariumId}`);
    const aquarium = await response.json();
    
    document.getElementById('aquariumName').textContent = aquarium.name;
    aquariumParams = aquarium.parameters;
    
    const paramsContainer = document.getElementById('parameters_inputs');
    paramsContainer.innerHTML = aquariumParams.map(p => `
        <div class="form-group">
            <label>${p.display_name} (${p.unit})</label>
            <input type="number" step="any" data-param="${p.name}" class="form-control" placeholder="Введите значение">
        </div>
    `).join('');
    
    const checkboxesContainer = document.getElementById('param_checkboxes');
    checkboxesContainer.innerHTML = aquariumParams.map(p => `
        <label class="checkbox-item">
            <input type="checkbox" value="${p.name}" class="param-checkbox" checked> ${p.display_name} (${p.unit})
        </label>
    `).join('');
    
    await loadRecommendations();
}

async function loadRecommendations() {
    const response = await fetch(`/api/recommendations/${aquariumId}`);
    const data = await response.json();
    const recDiv = document.getElementById('recommendations');
    
    if (data.has_issues && data.recommendations.length > 0) {
        recDiv.innerHTML = `
            <div class="recommendations">
                <h4>Рекомендации по уходу</h4>
                <ul>${data.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
            </div>
        `;
    } else {
        recDiv.innerHTML = '';
    }
}

async function loadMeasurements() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const selectedParams = getSelectedParams();
    
    let url = `/api/aquariums/${aquariumId}/measurements_pivot`;
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (selectedParams.length) params.push(`parameters=${selectedParams.join(',')}`);
    if (params.length) url += '?' + params.join('&');
    
    const response = await fetch(url);
    const data = await response.json();
    
    updateTable(data);
    updateChart(data);
}

function getSelectedParams() {
    return Array.from(document.querySelectorAll('.param-checkbox:checked')).map(cb => cb.value);
}

function updateTable(data) {
    const thead = document.getElementById('tableHeader');
    const tbody = document.getElementById('tableBody');
    
    let headerRow = '<tr><th>Дата</th>';
    data.parameters.forEach(param => {
        headerRow += `<th>${param.display_name} (${param.unit})</th>`;
    });
    headerRow += '</tr>';
    thead.innerHTML = headerRow;
    
    tbody.innerHTML = '';
    data.data.forEach(row => {
        let tr = '<tr>';
        tr += `<td>${row.date}</td>`;
        data.parameters.forEach(param => {
            let value = row[param.name];
            tr += `<td>${value !== null && value !== undefined ? value : '-'}</td>`;
        });
        tr += '</tr>';
        tbody.innerHTML += tr;
    });
}

function updateChart(data) {
    const ctx = document.getElementById('measurementChart').getContext('2d');
    if (currentChart) currentChart.destroy();
    
    const dates = data.data.map(d => d.date);
    const datasets = [];
    const colors = ['#0066cc', '#dc3545', '#28a745', '#ffc107', '#17a2b8', '#6f42c1', '#fd7e14', '#20c997', '#e83e8c', '#6610f2'];
    
    data.parameters.forEach((param, idx) => {
        const values = data.data.map(row => row[param.name]);
        datasets.push({
            label: param.display_name,
            data: values,
            borderColor: colors[idx % colors.length],
            backgroundColor: 'transparent',
            tension: 0.1,
            fill: false
        });
    });
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: { labels: dates, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' }, tooltip: { mode: 'index', intersect: false } },
            scales: { x: { title: { display: true, text: 'Дата' } }, y: { title: { display: true, text: 'Значение' } } }
        }
    });
}

window.showTab = function(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    if (tabId === 'history-tab') {
        loadMeasurements();
    }
};

window.addMeasurement = async function() {
    const date = document.getElementById('measurement_date').value;
    if (!date) {
        alert('Выберите дату');
        return;
    }
    
    const values = {};
    let hasError = false;
    
    document.querySelectorAll('[data-param]').forEach(input => {
        if (input.value) {
            const num = parseFloat(input.value);
            if (isNaN(num)) {
                alert(`Некорректное значение для ${input.previousElementSibling?.innerText || input.dataset.param}`);
                hasError = true;
                return;
            }
            if (num < 0) {
                alert(`Значение не может быть отрицательным: ${input.previousElementSibling?.innerText || input.dataset.param}`);
                hasError = true;
                return;
            }
            values[input.dataset.param] = num;
        }
    });
    
    if (hasError) return;
    
    if (Object.keys(values).length === 0) {
        alert('Введите хотя бы одно значение');
        return;
    }
    
    const formData = new URLSearchParams();
    formData.append('date_str', date);
    formData.append('values', JSON.stringify(values));
    
    try {
        const response = await fetch(`/api/aquariums/${aquariumId}/measurements`, { 
            method: 'POST', 
            body: formData 
        });
        const data = await response.json();
        if (response.ok) {
            window.location.reload();
        } else {
            alert(data.error || 'Ошибка при сохранении замера');
        }
    } catch (err) {
        alert('Ошибка соединения с сервером');
    }
};
window.applyFilter = function() {
    loadMeasurements();
};

window.exportData = function() {
    window.location.href = `/api/aquariums/${aquariumId}/export`;
};