document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', event => {
        event.preventDefault();
        
        const identifier = document.getElementById('identifier').value;
        const password = document.getElementById('password').value;

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                identifier: identifier,
                password: password
            })
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;  // Redirect to home page on successful login
            } else {
                alert('Login failed. Please check your username/email and password.');
            }
        })
        .catch(error => console.error('Error logging in:', error));
    });
});

