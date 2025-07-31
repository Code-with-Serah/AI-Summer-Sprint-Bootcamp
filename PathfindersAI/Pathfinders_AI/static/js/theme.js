document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    const initTheme = () => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateToggleIcon(savedTheme);
    };

    const updateToggleIcon = (theme) => {
        const icon = themeToggle.querySelector('i');
        if (!icon) return;
        
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            icon.style.color = '#ffd166';
        } else {
            icon.className = 'fas fa-moon';
            icon.style.color = 'white';
        }
    };

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateToggleIcon(newTheme);
    });

    initTheme();
});