document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');

    registerForm.addEventListener('submit', event => {
        event.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        fetch('/api/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        })
        .then(response => {
            if (response.ok) {
                window.location.href = 'login.html';  // Redirect to login page on successful signup
            } else {
                alert('Signup failed. Please check your details and try again.');
            }
        })
        .catch(error => console.error('Error signing up:', error));
    });
});