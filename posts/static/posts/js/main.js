// Добавьте этот код в конец вашего main.js

// Плавное появление элементов
document.addEventListener('DOMContentLoaded', () => {
    // Анимация постов
    const posts = document.querySelectorAll('.post');
    posts.forEach((post, index) => {
        post.style.animationDelay = `${index * 0.1}s`;
    });

    // Параллакс эффект для фона
    document.addEventListener('mousemove', (e) => {
        const x = (window.innerWidth - e.pageX) / 100;
        const y = (window.innerHeight - e.pageY) / 100;
        document.body.style.backgroundPosition = `${x}px ${y}px`;
    });
});