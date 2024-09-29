document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();

    // CSRF 토큰을 가져옵니다.
    const csrfToken = getCsrfToken();

    axios.post('/api/accounts/api/token/', {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    }, {
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        localStorage.setItem('access', response.data.access);
        localStorage.setItem('refresh', response.data.refresh);
        localStorage.setItem('user_id', response.data.user_id);
        localStorage.setItem('user_nickname', response.data.user_nickname);
        window.location.href = '/api/accounts/main/'
    })
    .catch(error => {
        console.error('로그인 실패.', error);
    });
});