import os
import requests
from datetime import datetime, timedelta
import openai
from openai import OpenAI
from dotenv import load_dotenv

CONSUMER_KEY = 'HUcIiU1Vx1zUbEzgVkz1f3ypAbQXzVnP'
CONSUMER_SECRET = 'rHo3SXLeP3BuqcD4'

load_dotenv()

my_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=my_api_key)

BASE_URL = 'https://app.ticketmaster.com/discovery/v2/'
def get_user_preferences():
    genre = input("What's your favorite genre of music? ")
    location = input("Enter your city: ") #might add option for state as well because of  common city names
    radius = input("Enter the radius (in miles) to search for events: ")
    return genre, location, radius
def get_events(location, genre, radius):
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    params = {
        'apikey': CONSUMER_KEY,
        'keyword': genre,
        'startDateTime': f"{start_date}T00:00:00Z",
        'endDateTime': f"{end_date}T23:59:59Z",
        'size': 20,
        'sort': 'date,asc',
        'segmentName': 'music',
        'classificationName': genre,
        'city': location,
        'radius': radius,
        'unit': 'miles'
    }
    response = requests.get(f"{BASE_URL}events.json", params=params)
    if response.status_code == 200:
        data = response.json()
        if '_embedded' in data and 'events' in data['_embedded']:
            return data['_embedded']['events']
    return []
def format_events(events):
    formatted_events = []
    for event in events:
        name = event['name']
        date = event['dates']['start']['localDate']
        time = event['dates']['start'].get('localTime', 'Time not specified')
        venue = event['_embedded']['venues'][0]['name']
        city = event['_embedded']['venues'][0]['city']['name']
        state = event['_embedded']['venues'][0]['state']['stateCode']
        classifications = event['classifications'][0]
        event_type = classifications['segment']['name']
        genre = classifications['genre']['name']
        formatted_events.append(f"Event: {name}, Genre: {genre}, Event Type: {event_type}, Date: {date}, Time: {time}, Venue: {venue}, Location: {city}, {state}")
    return formatted_events
def get_chatgpt_recommendations(songs, events):
    prompt = f"Given the user's last listened to artists '{songs}, and the concerts in thier area {events}, recommend the top 3 concerts they chould attend"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful event recommendatSion assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
def concert_recommendation_menu():
    user_genre, user_location, user_radius = get_user_preferences()
    events = get_events(user_location, user_genre, user_radius)
    if events:
        formatted_events = format_events(events)
        recommendations = get_chatgpt_recommendations(formatted_events, user_genre)
        #print("\nHere are some personalized event recommendations for you:")
        print(recommendations)
    else:
        print(f"Sorry, no events found within {user_radius} miles of {user_location} for the genre {user_genre} in the next 30 days.")