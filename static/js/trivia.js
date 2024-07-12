document.addEventListener('DOMContentLoaded', () => {
    const questionElement = document.getElementById('question');
    const optionsElement = document.getElementById('options');
    const resultElement = document.getElementById('result');
    const nextQuestionButton = document.getElementById('nextQuestion');

    function loadQuestion() {
        fetch('/get_trivia_question')
            .then(response => response.json())
            .then(data => {
                displayQuestion(data);
            })
            .catch(error => console.error('Error loading question:', error));
    }

    function displayQuestion(data) {
        questionElement.textContent = data.question;
        optionsElement.innerHTML = Object.entries(data.options).map(([letter, option]) => 
            `<button class="trivia-option button" data-answer="${letter}">${letter}) ${option}</button>`
        ).join('');
        resultElement.textContent = '';
        nextQuestionButton.style.display = 'none';
    }

    function submitAnswer(answer) {
        fetch('/answer_trivia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answer: answer })
        })
        .then(response => response.json())
        .then(data => {
            resultElement.textContent = data.message;
            if (data.status === 'correct') {
                loadLeaderboard(); // Update leaderboard if the answer is correct
            }
            nextQuestionButton.style.display = 'block';
        })
        .catch(error => console.error('Error submitting answer:', error));
    }

    function loadLeaderboard() {
        fetch('/get_leaderboard')
            .then(response => response.json())
            .then(data => {
                const leaderboardContent = document.getElementById('leaderboardContent');
                leaderboardContent.innerHTML = `
                    <ol>
                        ${data.map(item => `<li>${item.username}: ${item.score} points</li>`).join('')}
                    </ol>
                `;
            })
            .catch(error => console.error('Error loading leaderboard:', error));
    }

    optionsElement.addEventListener('click', (event) => {
        if (event.target.classList.contains('trivia-option')) {
            submitAnswer(event.target.dataset.answer);
        }
    });

    nextQuestionButton.addEventListener('click', loadQuestion);

    if (!questionElement.textContent.trim()) {
        loadQuestion();
    }
});
