document.addEventListener("DOMContentLoaded", function() {
    const postsList = document.getElementById('postsList');
    const searchInput = document.getElementById('searchInput');
    const categorySelect = document.getElementById('categorySelect');
    const sortSelect = document.getElementById('sortSelect');
    const prevPageButton = document.getElementById('prevPage');
    const nextPageButton = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');
    let currentPage = 1;
    let totalPages = 1;

    function formatDate(dateString) {
        return dateString.split('T')[0];
    }

    async function fetchPosts() {
        const searchQuery = encodeURIComponent(searchInput.value.trim());
        const category = categorySelect.value;
        const sortOption = sortSelect.value;

        try {
            const response = await axios.get('/api/posts/api/list/', {
                params: {
                    search: searchQuery,
                    category: category,
                    sort: sortOption,
                    page: currentPage
                }
            });

            if (response.status === 200) {
                const { posts, total_pages, current_page } = response.data;
                totalPages = total_pages;
                currentPage = current_page;
                renderPosts(posts);
                updatePaginationControls();
            } else {
                console.error("Failed to fetch posts, status code:", response.status);
            }
        } catch (error) {
            console.error("Error fetching posts:", error);
        }
    }

    function renderPosts(posts) {
        postsList.innerHTML = '';

        posts.forEach(post => {
            const postElement = document.createElement('div');
            const postId = post.id;
            postElement.classList.add('post');
            
            // 콘텐츠를 100자로 자르기
            const truncatedContent = post.content.length > 50 
                ? post.content.substring(0, 50) + '...' 
                : post.content;

            postElement.innerHTML = `
            <div class="list">
                <a href="/api/posts/${post.id}">
                    <img src="${post.image}" />
                    <div class="content">
                        <p id="post-title">${post.title}</p>
                        <p id="post-content">${truncatedContent}</p>
                        <div class="author-create-like">
                            <p>${post.author_nickname}</p>
                            <p>${formatDate(post.created_at).toLocaleString()}</p>
                            <p>좋아요 ${post.like_count}</p>
                        </div>
                    </div>
                </a>
            </div>
            `;
            postsList.appendChild(postElement);
        });
    }

    function updatePaginationControls() {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevPageButton.disabled = currentPage <= 1;
        nextPageButton.disabled = currentPage >= totalPages;
    }

    prevPageButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchPosts();
        }
    });

    nextPageButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            fetchPosts();
        }
    });

    searchInput.addEventListener('input', fetchPosts);
    categorySelect.addEventListener('change', fetchPosts);
    sortSelect.addEventListener('change', fetchPosts);

    fetchPosts();
});
