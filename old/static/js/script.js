let userChart = null;

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

function renderChart(data) {
    const container = $('#chart-container').empty();
    const radius = 150;
    const centerX = 160;
    const centerY = 160;

    data.planets.forEach(planet => {
        const angle = (planet.longitude - 90) * Math.PI / 180;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        const icon = $('<img>')
            .attr('src', `/static/icons/${planet.name.toLowerCase()}.png`)
            .addClass('planet-icon')
            .css({ left: `${x - 12}px`, top: `${y - 12}px` });
        container.append(icon);
    });
}

function displayInsights(data) {
    $.post('/calculate_chart', JSON.stringify(data), function(response) {
        const insights = generateInsights(response); // This is handled server-side now
        $('#insights').html(insights.map(i => `<p>${i}</p>`).join(''));
    }, 'json');
}

// Birth Chart Form Submission
$('#birth-form').submit(function(e) {
    e.preventDefault();
    const data = {
        date: formatDate($('#date').val()),
        time: $('#time').val(),
        location: $('#location').val(),
        timezone: $('#timezone').val()
    };

    $.ajax({
        url: '/calculate_chart',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            userChart = response;
            renderChart(response);
            displayInsights(data);
            $('#chart-display, #daily-horoscope, #compatibility').show();
        },
        error: function() {
            alert('Error generating chart. Please check your inputs.');
        }
    });
});

// Daily Horoscope
$('#get-daily').click(function() {
    if (!userChart) return;
    $.ajax({
        url: '/daily_horoscope',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ birth_chart: userChart }),
        success: function(response) {
            $('#daily-insights').html(response.insights.map(i => `<p>${i}</p>`).join(''));
        }
    });
});

// Compatibility Form Submission
$('#compat-form').submit(function(e) {
    e.preventDefault();
    const compatData = {
        date: formatDate($('#compat-date').val()),
        time: $('#compat-time').val(),
        location: $('#compat-location').val(),
        timezone: $('#compat-timezone').val()
    };

    $.post('/calculate_chart', JSON.stringify(compatData), function(chart2) {
        $.ajax({
            url: '/compatibility',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ chart1: userChart, chart2: chart2 }),
            success: function(response) {
                $('#compat-result').html(`<p>Score: ${response.score}%</p><p>${response.insight}</p>`);
            }
        });
    }, 'json');
});