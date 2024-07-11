document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');

    registerForm.addEventListener('submit', event => {
        event.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // Updated content type for JSON data
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();  // Assuming backend returns JSON with success message or other data
            } else {
                throw new Error('Signup failed.');
            }
        })
        .then(data => {
            // Handle success (optional)
            console.log('Signup successful:', data);
            window.location.href = '/login';  // Redirect to login page after successful signup
        })
        .catch(error => {
            console.error('Error signing up:', error);
            alert('Signup failed. Please check your details and try again.');  // Display error message to user
        });
    });
});
