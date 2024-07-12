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
            `<button class="trivia-option" data-answer="${letter}">${letter}) ${option}</button>`
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
            nextQuestionButton.style.display = 'block';
        })
        .catch(error => console.error('Error submitting answer:', error));
    }

    optionsElement.addEventListener('click', (event) => {
        if (event.target.classList.contains('trivia-option')) {
            submitAnswer(event.target.dataset.answer);
        }
    });

    nextQuestionButton.addEventListener('click', loadQuestion);

    // Only load a new question if there isn't one already displayed
    if (!questionElement.textContent.trim()) {
        loadQuestion();
    }
});
