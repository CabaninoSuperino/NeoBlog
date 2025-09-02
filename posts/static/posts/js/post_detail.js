document.addEventListener("DOMContentLoaded", () => {
    const likeBtn = document.getElementById("like-btn");
    if (!likeBtn) return;

    const postId = likeBtn.dataset.postId;
    const likeIcon = likeBtn.querySelector('i');
    const likeCount = document.getElementById("like-count");
    const viewsCount = document.getElementById("views-count");

    // Анимация счетчиков
    function animateCounter(element, newValue) {
        if (!element) return;

        const start = parseInt(element.textContent);
        const duration = 600;
        const startTime = performance.now();

        function update(time) {
            const elapsed = time - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const value = Math.floor(start + (newValue - start) * progress);
            element.textContent = value;

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        requestAnimationFrame(update);
    }

    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Отправить просмотр
    fetch(`/api/posts/${postId}/view/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.views_count !== undefined && viewsCount) {
            animateCounter(viewsCount, data.views_count);
        }
    })
    .catch(error => console.error('View error:', error));

    // Обработка лайков
    likeBtn.addEventListener("click", () => {
        fetch(`/api/posts/${postId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status) {
                // Обновление иконки
                if (data.status === 'liked') {
                    likeIcon.classList.replace('far', 'fas');
                } else {
                    likeIcon.classList.replace('fas', 'far');
                }

                // Анимация
                likeIcon.classList.add('pulse');
                setTimeout(() => {
                    likeIcon.classList.remove('pulse');
                }, 600);

                // Обновление счетчика
                if (likeCount) {
                    animateCounter(likeCount, data.like_count);
                }
            }
        })
        .catch(error => console.error('Like error:', error));
    });
});