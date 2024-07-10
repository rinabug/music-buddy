document.addEventListener('DOMContentLoaded', () => {
    const spotifyLoginButton = document.getElementById('spotify-login');

    spotifyLoginButton.addEventListener('click', () => {
        // Redirect to Spotify login page or handle Spotify OAuth flow
        window.location.href = '/api/spotify-login';  // Adjust the URL to match backend endpoint
    });
});