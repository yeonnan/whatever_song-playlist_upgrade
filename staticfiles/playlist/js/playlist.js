// 검색 결과 가져오기
function searchPlaylist(query) {
    axios.get(`/api/playlist/search/?query=${query}`)
        .then(response => {
            displayPlaylist(response.data);
            checkUserZzimPlaylists();
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}

// 플레이리스트 표시
function displayPlaylist(playlists) {
    const container = document.getElementById('playlist-container');
    container.innerHTML = ''; // 기존 내용을 지움

    playlists.forEach(playlist => {
        const item = document.createElement('div');
        item.className = 'playlist-item';
        
        // 이미지 URL이 존재하는지 확인하고 설정
        const imageUrl = playlist.image_url || 'https://via.placeholder.com/150';
        
        // playlist.id를 고유 식별자로 사용
        const playlistId = playlist.id;
        item.innerHTML = `
            <a href="${playlist.link}" target="_blank">
                <img src="${imageUrl}" alt="${playlist.name}">
                <div class="playlist-info">
                    <h2>${playlist.name}</h2>

                </div> 
            </a>

            <button class="zzim-button" data-id="${playlistId}">♡</button>



        `;
        container.appendChild(item);
    });

    // 찜 버튼
    const zzimButtons = document.querySelectorAll('.zzim-button');
    zzimButtons.forEach(button => {
            button.addEventListener('click', function(event) {
            event.preventDefault();
            const playlistId = this.getAttribute('data-id');
            toggleZzim(playlistId, this);
        });
    });
}

// 로그인 여부를 확인하고, 로그인 된 상태라면 해당 user의 찜한 playlist.id를 가져와 일치하는 찜 버튼의 설정을 바꿈
function checkUserZzimPlaylists() {
    const csrfToken = getCsrfToken();
    const access = localStorage.getItem('access');
    axios.get('/api/playlist/user-zzim/', {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${access}`
        }
    })
    .then(response => {
        const zzimPlaylists = response.data;
        const zzimPlaylistIds = zzimPlaylists.map(aaa => aaa.playlist_id); // 모든 값을 문자열로 변환
        const zzimButtons = document.querySelectorAll('.zzim-button');
        zzimButtons.forEach(button => {
            const playlistId = button.getAttribute('data-id');
            if (zzimPlaylistIds.includes(playlistId)) {
                button.textContent = '♥️'; // 이미 찜한 버튼 변경
            }
        });
    })
    .catch(error => {
        console.error('Error fetching user zzim playlists:', error);
    });
}

// 찜하기 상태 변경. 
function toggleZzim(playlistId, button) {
    if (!playlistId) {
        console.error('Playlist ID is undefined');
        return;
    }
    const csrfToken = getCsrfToken();
    const access = localStorage.getItem('access');
    axios.post(`/api/playlist/zzim/${playlistId}/`, playlistId, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${access}` 
        }
    })
    .then(response => {
        if (response.data.message.includes('추가')) {
            button.textContent = '♥️';
        } else {
            button.textContent = '♡';
        }
    })
    .catch(error => {
        if (error.response && error.response.status === 401) {
            alert('로그인이 필요합니다.');
            window.location.href = '/api/accounts/login/';
        } else {
            console.error('Error toggling zzim:', error);
        }
    });
}

// 기본 플레이리스트 가져오기

function fetchPlaylists() {
    const csrfToken = getCsrfToken();
    axios.get('/api/playlist/data/', {
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })    
        .then(response => {
            displayPlaylist(response.data);
            checkUserZzimPlaylists();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// 페이지 로드 시 기본 플레이리스트를 가져옴
document.addEventListener('DOMContentLoaded', function() {
    fetchPlaylists();
    // 검색 
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            const query = searchInput.value;
            if (query) {
                searchPlaylist(query);
            } else {
                fetchPlaylists(); // 검색어가 없으면 기본 플레이리스트를 다시 가져옴
            }
        }
    });
});

