// CSRF 토큰을 가져오는 전역 함수
function getCsrfToken() {
    return document.getElementById('csrf-token').value;
}

// JWT 토큰을 디코딩하는 함수
function parseJwt(token) {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        return null;
    }
}

// Access token을 새로고침하는 함수
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh');
    try {
        const response = await axios.post('/api/accounts/api/token/refresh/', { refresh: refreshToken });
        const newAccessToken = response.data.access;
        localStorage.setItem('access', newAccessToken);
        return newAccessToken;
    } catch (error) {
        console.error('Error refreshing token:', error);
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_nickname');
        if (window.location.pathname !== '/api/accounts/login/') {
            window.location.href = '/api/accounts/login/';
        }
        throw error;
    }
}

function isExcludedUrl(url, patterns) {
    return patterns.some(pattern => {
        const regex = new RegExp(pattern.replace(/<int:\w+>/g, '\\d+'));
        return regex.test(url);
    });
}

// Axios 요청 인터셉터를 설정하여 자동으로 토큰을 갱신하는 함수
axios.interceptors.request.use(
    async config => {
        // 특정 URL을 제외
        const excludedUrls = [
        '/api/accounts/main/',
        '/api/accounts/signup/', 
        '/api/accounts/api/token/', 
        '/api/accounts/login/', 
        '/api/accounts/logout/', 
        '/api/accounts/api/signup/', 
        '/api/playlist/list/', 
        '/api/playlist/data/', 
        '/api/playlist/search/', 
        '/api/playlist/zzim/\\d+',
        '/api/posts/api/list/',
        '/api/posts/list/', 
        '/api/posts/api/\\d+', 
        '/api/posts/\\d+'];
        if (isExcludedUrl(config.url, excludedUrls)) {
            return config;
        }


        let accessToken = localStorage.getItem('access');  // let으로 선언하여 재할당 가능
        const tokenData = parseJwt(accessToken);
        const now = Math.ceil(Date.now() / 1000);

        // 토큰이 만료되었는지 확인
        if (tokenData.exp < now) {
            accessToken = await refreshAccessToken();  // 만료된 경우 새 토큰 발급
        }

        config.headers['Authorization'] = 'Bearer ' + accessToken;
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

function checkLoginStatus() {
    const accessToken = localStorage.getItem('access');
    const loginLogoutLink = document.getElementById('login-logout-link');
    const signupProfileLink = document.getElementById('signup-profile-link');
    if (accessToken) {
        loginLogoutLink.textContent = 'Logout';
        loginLogoutLink.style.cursor = 'pointer';
        loginLogoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
        const userId = localStorage.getItem('user_id');
        signupProfileLink.textContent = 'Profile';
        signupProfileLink.href = `/api/accounts/profile/${userId}/`;
    } else {
        loginLogoutLink.textContent = 'Login';
        loginLogoutLink.href = '/api/accounts/login/';
        signupProfileLink.textContent = 'Signup';
        signupProfileLink.href = '/api/accounts/signup/';
    }
}

function logout() {
    const refreshToken = localStorage.getItem('refresh');
    const csrfToken = getCsrfToken();
    axios.post('/api/accounts/logout/', { refresh: refreshToken }, {
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_nickname');
        window.location.href = '/api/accounts/login/';
    })
    .catch(error => {
        console.error('로그아웃 실패.', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});
