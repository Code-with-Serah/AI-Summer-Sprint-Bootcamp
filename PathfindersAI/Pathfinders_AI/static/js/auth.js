document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.auth-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        
        if (!email || !password) {
            alert('Please fill in all fields');
            return;
        }

        console.log('Login attempt with:', { email, password });
        
        window.location.href = 'chat.html';
    });
});