function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
    
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    if (tabId === 'history-tab') {
        loadMeasurementsTable();
        applyFilter();
    }
}

function loadRecommendations() {
    const aquariumId = window.location.pathname.split('/').pop();
    fetch(`/api/recommendations/${aquariumId}`)
        .then(response => response.json())
        .then(data => {
            const recDiv = document.getElementById('recommendations');
            if (recDiv && data.has_issues && data.recommendations.length > 0) {
                let html = '<div class="recommendations"><h4>Рекомендации</h4><ul>';
                data.recommendations.forEach(rec => {
                    html += `<li>${rec}</li>`;
                });
                html += '</ul></div>';
                recDiv.innerHTML = html;
            } else if (recDiv) {
                recDiv.innerHTML = '';
            }
        });
}

function addMeasurement() {
    const date = document.getElementById('measurement_date').value;
    const values = {};
    
    document.querySelectorAll('[data-param]').forEach(input => {
        if (input.value) {
            values[input.dataset.param] = parseFloat(input.value);
        }
    });
    
    fetch(window.location.pathname + '/measurement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ date_str: date, values: JSON.stringify(values) })
    }).then(() => {
        window.location.reload();
    });
}

function exportData() {
    window.location.href = window.location.pathname + '/export';
}

function deleteAquarium(aquariumId) {
    if (confirm('Удалить аквариум? Все данные будут потеряны.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/aquarium/delete/${aquariumId}`;
        document.body.appendChild(form);
        form.submit();
    }
}

let currentParameters = [];
let currentChart = null;

function loadMeasurementsTable() {
    const aquariumId = window.location.pathname.split('/').pop();
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    let url = `/api/measurements_pivot/${aquariumId}`;
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (params.length) url += '?' + params.join('&');
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            currentParameters = data.parameters;
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
        });
}

function applyFilter() {
    loadMeasurementsTable();
    const aquariumId = window.location.pathname.split('/').pop();
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    updateChart(aquariumId, startDate, endDate);
}

function updateChart(aquariumId, startDate, endDate) {
    let url = `/api/measurements/${aquariumId}`;
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (params.length) url += '?' + params.join('&');
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            fetch('/api/parameters')
                .then(res => res.json())
                .then(parameters => {
                    const ctx = document.getElementById('measurementChart').getContext('2d');
                    if (currentChart) {
                        currentChart.destroy();
                    }
                    
                    const paramNames = [...new Set(data.map(d => d.parameter))];
                    const dates = [...new Set(data.map(d => d.date))].sort();
                    
                    const datasets = [];
                    const colors = ['#0066cc', '#dc3545', '#28a745', '#ffc107', '#17a2b8', '#6f42c1', '#fd7e14', '#20c997', '#e83e8c', '#6610f2'];
                    
                    paramNames.forEach((paramName, idx) => {
                        const paramInfo = parameters.find(p => p.name === paramName);
                        const paramData = data.filter(d => d.parameter === paramName);
                        const dataMap = {};
                        paramData.forEach(d => { dataMap[d.date] = d.value; });
                        
                        const chartData = dates.map(date => dataMap[date] !== undefined ? dataMap[date] : null);
                        
                        datasets.push({
                            label: paramInfo ? paramInfo.display_name : paramName,
                            data: chartData,
                            borderColor: colors[idx % colors.length],
                            backgroundColor: 'transparent',
                            tension: 0.1,
                            fill: false
                        });
                    });
                    
                    currentChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: dates,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom' },
                                tooltip: { mode: 'index', intersect: false }
                            },
                            scales: {
                                x: { title: { display: true, text: 'Дата' } },
                                y: { title: { display: true, text: 'Значение' } }
                            }
                        }
                    });
                });
        });
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/aquarium/') && !window.location.pathname.includes('/create')) {
        loadRecommendations();
        loadMeasurementsTable();
        const aquariumId = window.location.pathname.split('/').pop();
        updateChart(aquariumId, null, null);
    }
});