document.addEventListener('DOMContentLoaded', function() {
    const inputFile = document.getElementById('input_file');
    const fileNameDisplay = document.getElementById('file-name');

    inputFile.addEventListener('change', function() {
        if (inputFile.files.length > 0) {
            fileNameDisplay.innerText = inputFile.files[0].name;
        } else {
            fileNameDisplay.innerText = '선택된 파일 없음';
    }});
});

document.getElementById('inputForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const csrfToken = getCsrfToken();
    const access = window.localStorage.getItem('access');
    if (!access) {
        alert('로그인이 필요합니다.');
        window.location.href = '/api/accounts/login/';
        return;
    }
    const youtubeUrl = document.getElementById('youtube_url').value;
    const inputFile = document.getElementById('input_file').files[0];
    const formData = new FormData();
    formData.append('youtube_url', youtubeUrl);
    formData.append('input_file', inputFile);


    axios.post('/api/coach/api/input/', formData,{ 
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${access}`
        }
    })
    .then(response => {
        const data = response.data;
        const dataId = data.id;
        window.location.href = `/api/coach/result/${dataId}/`;
    })
    .catch(error => {
            console.error(error);        
    });
});