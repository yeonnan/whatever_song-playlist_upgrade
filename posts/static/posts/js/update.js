// URL 경로에서 postId를 추출하는 함수
function extractPostIdFromUrl() {
    const path = window.location.pathname; // 현재 URL 경로를 가져옴
    const segments = path.split('/'); // 경로를 '/'로 분할하여 배열로 만듦
    return segments[segments.length - 3]; // 마지막에서 두 번째 요소가 postId임
}

// postId를 URL 경로에서 가져옴
const postId = extractPostIdFromUrl();
const csrfToken = getCsrfToken();
const access = localStorage.getItem('access');  // 저장된 토큰 가져오기

function loadPost() {
    if (!access) {
        console.error('No access token found');
        return;
    }
    axios.get(`/api/posts/api/${postId}/`, {
        headers: {
            'Authorization': `Bearer ${access}`  // 인증 토큰을 헤더에 추가
        }
    })
    .then(response => {
        const data = response.data.data;
        document.getElementById('post-title').value = data.title;
        document.getElementById('post-content').value = data.content;
        document.getElementById('song-link').value = data.link;
        if (data.image) {
            document.getElementById("file-name").src = data.image;
            document.getElementById('file-input').src = data.image;
        }
    })
    .catch(error => {
        console.error('Failed to load post:', error);
    });
}

loadPost();

document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');

    imageInput.addEventListener('change', function() {
        if (imageInput.files.length > 0) {
            fileNameDisplay.innerText = imageInput.files[0].name;
        } else {
            fileNameDisplay.innerText = fileNameDisplay.files[0];
    }});
});

document.getElementById('update-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData();
        formData.append("title", document.getElementById('post-title').value);
        formData.append("content", document.getElementById('post-content').value);
        const postUrl = document.getElementById('song-link');
        if (postUrl.value) {
            formData.append('link', postUrl.value);
        }
        const imageFile = document.getElementById('file-input').files[0];
        if (imageFile) { 
            formData.append('image', imageFile);
        }
    axios.put(`/api/posts/api/${postId}/`, formData, {
        headers: {
            'Authorization': `Bearer ${access}`,  // 인증 토큰을 헤더에 추가
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        window.location.href = `/api/posts/${postId}/`
    })
    .catch(error => {
        console.error(error);
    });
})


