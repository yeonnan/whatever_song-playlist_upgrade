const access = window.localStorage.getItem('access');
if (!access) {
    window.location.href = "/api/accounts/login/";
}

document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');

    imageInput.addEventListener('change', function() {
        if (imageInput.files.length > 0) {
            fileNameDisplay.innerText = imageInput.files[0].name;
        } else {
            fileNameDisplay.innerText = '선택된 파일 없음';
    }});
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('create-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const userId = window.localStorage.getItem('user_id');
        const userNickname = window.localStorage.getItem('user_nickname');
        const formData = new FormData();
        formData.append('title', document.getElementById('post-title').value);
        formData.append('author', userId);
        formData.append('author_nickname', userNickname);
        formData.append('content', document.getElementById('post-content').value);
        const postUrl = document.getElementById('post-url');
        if (postUrl.value) {
            formData.append('link', postUrl.value);
        }

        const postCategory = document.getElementById('post-category')
        if (postCategory.value != '----') {
            formData.append('category', postCategory.value);
        }

        const imageInput = document.getElementById('file-input');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }


        // CSRF 토큰을 가져옵니다.
        const csrfToken = getCsrfToken();

        axios.post('/api/posts/api/create/', formData, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Authorization': `Bearer ${access}`
            }
        })
        .then(response => {
            window.location.href = '/api/posts/list/'
        })
        .catch(error => {
            console.log("error: ", response.error);
            console.error('게시 실패.', error);
            alert("게시 실패: ", error.response.data);
        });
    });
});