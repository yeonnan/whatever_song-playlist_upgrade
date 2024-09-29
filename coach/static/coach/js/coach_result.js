document.addEventListener("DOMContentLoaded", function() {
    const pk = window.location.pathname.split('/').slice(-2, -1)[0];
    function loadResult() {
        const csrfToken = getCsrfToken();
        const access = localStorage.getItem('access');
        if (!access) {
            console.error('No access token found');
            return;
        }
        axios.get(`/api/coach/api/result/${pk}/`, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Authorization': `Bearer ${access}`
            }
        })
        .then(response => {
            const data = response.data;
            document.getElementById('title').innerText = data.youtube_title;
            document.getElementById('high_pitch_score').innerText = data.high_pitch_score;
            document.getElementById('low_pitch_score').innerText = data.low_pitch_score;
            document.getElementById('pitch_score').innerText = data.pitch_score;
            document.getElementById('message').innerText = data.message;
            if (data.graph) {
                document.getElementById('graph').src = data.graph;
            }
        })
        .catch(error => console.error('Error:', error));
    }
    loadResult();
});