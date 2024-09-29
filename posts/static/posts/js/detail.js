    // URL 경로에서 postId를 추출하는 함수
    function extractPostIdFromUrl() {
        const path = window.location.pathname; // 현재 URL 경로를 가져옴
        const segments = path.split('/'); // 경로를 '/'로 분할하여 배열로 만듦
        return segments[segments.length - 2]; // 마지막에서 두 번째 요소가 postId임
    }

    // postId를 URL 경로에서 가져옴
    const postId = extractPostIdFromUrl();



    function formatDate(dateString) {
        return dateString.split('T')[0]; // 'T'로 분할하여 첫 번째 요소만 반환
    }

    document.addEventListener('DOMContentLoaded', async function() {
        const access = window.localStorage.getItem('access');
        const headers = access ? { 'Authorization': `Bearer ${access}` } : {};
        const userId = window.localStorage.getItem('user_id');
        if (!postId) {
            console.error('postId를 URL 경로에서 추출할 수 없습니다.');
            return;
        }

    try {
        // 게시물 데이터를 서버에서 가져옴
        const response = await axios.get(`/api/posts/api/${postId}/`, {
            headers
        });
        const post = response.data.data;
        const like = response.data.like;
        const postAuthor = document.getElementById('post-author');
        const postLink = document.getElementById('post-link');
        const postLinkBox = document.querySelector('.post-link');
        const editPostButton = document.getElementById('update');
        const authorId = post.author;
        // HTML 요소에 게시물 데이터를 채움
        document.getElementById('post-title').innerText = post.title;
        document.getElementById('post-content').innerText = post.content;
        if (post.link) {
            postLink.href = post.link;
            postLink.textContent = '바로가기';
        }
        else {
            postLinkBox.style.display = "none";
            postLink.style.display = "none";
        }
        postAuthor.href = `/api/accounts/profile/${authorId}/`
        postAuthor.textContent = `작성자: ${post.author_nickname}`;
        document.getElementById('post-created').innerText = `작성일: ${formatDate(post.created_at)}`;
        document.getElementById('like-count').innerText = ` ${post.like_count}`;
        document.getElementById('comment-count').innerText = `💬 ${post.comments_count}`
        if (userId == authorId) {            
            editPostButton.href = `/api/posts/${postId}/update/`;
            editPostButton.style.display = "block";
            //삭제기능 추가
            document.getElementById('delete-button').addEventListener('click', function() {
                const access = window.localStorage.getItem('access');
                const csrfToken = getCsrfToken();
                if(confirm('삭제하시겠습니까?')) {
                    axios.delete(`/api/posts/api/${postId}/`, {
                        headers: {
                            'Authorization': `Bearer ${access}`,
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => {
                        window.location.href = '/api/posts/list/'
                    })
                    .catch(error => {
                        console.error('삭제 실패.', error);
                    });
                }
            })
            document.getElementById('delete-button').style.display = 'block';
        } else {
            editPostButton.style.display = "none";
            document.getElementById('delete-button').style.display = 'none';
            }
        if (post.image) {
            document.getElementById('post-img').src = post.image; 
        }
        else { 
            console.warn('No image available for this post.'); 
        }
        
        const unlikeButton = document.getElementById("unlike");
        const likeButton = document.getElementById("like");
        if (like) {
            likeButton.style.visibility = "hidden";
            unlikeButton.style.visibility = "visible";
        } 
        else {
            likeButton.style.visibility = "visible";
            unlikeButton.style.visibility = "hidden";
        }
        




        // 댓글 목록을 처리함
        const commentsList = document.getElementById('comment');
        commentsList.innerHTML = '';
        post.comments.forEach(comment => {
            // 각 댓글 항목을 생성함
            const userId = window.localStorage.getItem('user_id');
            const commentItem = document.createElement('div');
            commentItem.className = 'comment-wrap'
            commentItem.innerHTML = `
                <a href="/api/accounts/profile/${comment.user}">
                    <img src="${comment.user_image}">
                </a>
                <div class="comment-content">
                    <div class="author-update-delete">
                        <p class="comment-auhtor">${comment.user_nickname}</p>
                        <div class="btn">
                            <button id="buttonincomment" onclick="editComment(${comment.id})">수정</button>
                            <button id="buttonincomment" onclick="deleteComment(${comment.id})">삭제</button>
                        </div>
                    </div>
                    <p class="comment-content">${comment.content}</p>
                    <p>${formatDate(comment.created_at)}</p>
                </div>
            `;
            const commentButtons = commentItem.querySelectorAll('#buttonincomment');
            commentButtons.forEach(button => {
                if (userId != comment.user) {
                button.style.display = "none";
                }
            commentsList.appendChild(commentItem);
            });
        });
    } catch (error) {
        // 데이터를 가져오는 중 오류가 발생하면 오류를 콘솔에 출력함
        console.error('게시물 데이터를 가져오는 중 오류 발생:', error);
    }
});


document.getElementById("like").addEventListener("click", function() {
    const access = window.localStorage.getItem('access');
    const userId = window.localStorage.getItem('user_id');
    if (!userId) {
        window.location.href = '/api/accounts/login';
    }
    // CSRF 토큰을 가져옵니다.
    const csrfToken = getCsrfToken(); 
    const data = { post_id: postId, user_id: userId };

    axios.post(`/api/posts/${postId}/like/`, data, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${access}`
        }
    })
    .then(response => {
        window.location.href = `/api/posts/${postId}/`; 
    })
    .catch(error => {
        console.log("error: ", error);
        console.error('몰라용~', error);
    });
});

document.getElementById("unlike").addEventListener("click", function() {
    const access = window.localStorage.getItem('access');
    const userId = window.localStorage.getItem('user_id');
    if (!userId) {
        window.location.href = '/api/accounts/login';
    }
    // CSRF 토큰을 가져옵니다.
    const csrfToken = getCsrfToken(); 
    const data = { post_id: postId, user_id: userId };

    axios.post(`/api/posts/${postId}/like/`, data, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${access}`
        }
    })
    .then(response => {
        
        window.location.href = `/api/posts/${postId}/`;
    })
    .catch(error => {
        console.log("error: ", error);
        console.error('몰라용~', error);
    });
});

document.getElementById("comment-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const access = window.localStorage.getItem('access');
    const userId = window.localStorage.getItem('user_id');
    const userNickname = window.localStorage.getItem('user_nickname');
    const formData = new FormData();
    formData.append('content', document.getElementById('comment-content').value);
    formData.append('user', userId);
    formData.append('user_nickname', userNickname);

    const csrfToken = getCsrfToken();

    axios.post(`/api/posts/api/${postId}/`, formData, {
        headers: {
            'Authorization': `Bearer ${access}`,
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        window.location.href = `/api/posts/${postId}/`;
    })
    .catch(error => {
        console.error('작성 실패.', error);
    })
})

function deleteComment(commentId) {
    if (!confirm("댓글을 삭제하시겠습니까?")) {
        return;
    }

    const csrfToken = getCsrfToken();

    axios.delete(`/api/posts/api/comments/${commentId}/`, {
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        window.location.reload();
    })
    .catch(error => {
        console.error('댓글 삭제 실패.', error);
    });
}

async function editComment(commentId, currentContent) {
    const newContent = prompt("새로운 댓글 내용을 입력하세요:", currentContent);
    if (newContent === null) {
        return; // 수정 취소
    }

    const csrfToken = getCsrfToken();
    const access = window.localStorage.getItem('access');
    
    const formData = new FormData();
    formData.append('content', newContent);

    try {
        await axios.put(`/api/posts/api/comments/${commentId}/`, formData, {
            headers: {
                'Authorization': `Bearer ${access}`,
                'X-CSRFToken': csrfToken
            }
        });
        window.location.reload();
    } catch (error) {
        console.error('댓글 수정 실패:', error);
    }
}

