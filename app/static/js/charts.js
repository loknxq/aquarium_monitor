let chartInstance = null;

function createChart(canvasId, data, parameters, filterParams) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    const filteredData = filterParams && filterParams.length > 0 
        ? data.filter(d => filterParams.includes(d.parameter))
        : data;
    
    const paramNames = [...new Set(filteredData.map(d => d.parameter))];
    const dates = [...new Set(filteredData.map(d => d.date))].sort();
    
    const datasets = [];
    const colors = ['#0066cc', '#dc3545', '#28a745', '#ffc107', '#17a2b8', '#6f42c1', '#fd7e14', '#20c997', '#e83e8c'];
    
    paramNames.forEach((paramName, idx) => {
        const paramInfo = parameters.find(p => p.name === paramName);
        const paramData = filteredData.filter(d => d.parameter === paramName);
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
    
    chartInstance = new Chart(ctx, {
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
}

function updateChartWithFilter(aquariumId, startDate, endDate, filterParams) {
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
                    createChart('measurementChart', data, parameters, filterParams);
                });
        });
}