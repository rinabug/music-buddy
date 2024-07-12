import sqlite3
import random
from openai import OpenAI
import os
import re

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def create_leaderboard_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        score INTEGER DEFAULT 0,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    ''')
    conn.commit()

def update_score(conn, username, points):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO leaderboard (username, score) 
    VALUES (?, ?)
    ON CONFLICT(username) 
    DO UPDATE SET score = score + ?
    ''', (username, points, points))
    conn.commit()

def get_leaderboard(conn):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT username, score 
    FROM leaderboard 
    ORDER BY score DESC 
    LIMIT 10
    ''')
    return [{"username": row[0], "score": row[1]} for row in cursor.fetchall()]

def generate_trivia_question(artist):
    prompt = f"Generate a music trivia question "
    if artist:
        prompt += f"about the artist {artist} "
    prompt += "with four multiple-choice options. Format the response as: Question\\n A) Option\\n B) Option\\n C) Option\\n D) Option\\n Correct Answer: Letter"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a music trivia expert."},
            {"role": "user", "content": prompt}
        ]
    )
    
    question_data = response.choices[0].message.content
    pattern = r"Question\s*(.*)\s*A\)\s*(.*)\s*B\)\s*(.*)\s*C\)\s*(.*)\s*D\)\s*(.*)\s*Correct Answer:\s*([A-D])"
    match = re.match(pattern, question_data, re.DOTALL)

    if match:
        question = match.group(1).strip()
        options = {
            'A': match.group(2).strip(),
            'B': match.group(3).strip(),
            'C': match.group(4).strip(),
            'D': match.group(5).strip()
        }
        correct_answer = match.group(6).strip()
        return {'question': question, 'options': options, 'correct_answer': correct_answer}
    else:
        print("Error. Unable to parse the question data.")
        return None

def play_trivia(conn, username):
    print("\nWelcome to Trivia!")
    score = 0
    num_questions = 5

    for _ in range(num_questions):
        #In real implementation, will use user's listening history
        question_data = generate_trivia_question("Billie Eilish")
        
        print(question_data['question'])
        for key, value in question_data['options'].items():
            print(f"{key}) {value}")
        user_answer = input("Your answer (A/B/C/D): ").upper()

        if user_answer == question_data['correct_answer']:
            print("Correct!")
            score += 1
        else:
            print(f"Sorry, the correct answer was {question_data['correct_answer']}")

    print(f"\nYou scored {score} out of {num_questions}")
    update_score(conn, username, score)

def leaderboard_trivia_menu(conn, username):
    create_leaderboard_table(conn)

    while True:
        print("\nLeaderboard and Trivia Menu:")
        print("1. View Leaderboard")
        print("2. Play Trivia")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            leaderboard = get_leaderboard(conn)
            print("\nTop 10 Leaderboard:")
            for rank, (user, score) in enumerate(leaderboard, 1):
                print(f"{rank}. {user}: {score} points")
        elif choice == '2':
            play_trivia(conn, username)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")
