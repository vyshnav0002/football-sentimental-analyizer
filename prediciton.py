import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), '.env'))

# Get environment variables
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Debug check
print("Environment variables loaded successfully")


if None in (EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL, NEWS_API_KEY):
    raise ValueError("Missing environment variables. Check your .env file.")

# New: Fetch football news from NewsAPI
def get_football_news(api_key):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'football',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 10,
        'apiKey': api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] != 'ok':
            print(f"NewsAPI Error: {data.get('message', 'Unknown error')}")
            return []

        headlines = [article['title'] for article in data['articles']]
        return headlines

    except Exception as e:
        print(f"Error fetching football news: {e}")
        return []

def analyze_sentiment(headlines):
    results = []
    positive, negative, neutral = 0, 0, 0
    for headline in headlines:
        blob = TextBlob(headline)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            sentiment = "Positive"
            positive += 1
        elif polarity < 0:
            sentiment = "Negative"
            negative += 1
        else:
            sentiment = "Neutral"
            neutral += 1
        results.append(f"{sentiment}: {headline} (Polarity: {polarity:.2f})")

    total = positive + negative + neutral or 1
    summary = f"Sentiment Summary: {positive/total*100:.1f}% Positive, {negative/total*100:.1f}% Negative, {neutral/total*100:.1f}% Neutral"
    return results, summary

def send_email(headlines, summary):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"Daily Football News Summary - {datetime.now().strftime('%Y-%m-%d')}"

    body = "📰 Daily Football News and Sentiment Analysis:\n\n"
    body += "\n".join(headlines) + "\n\n" + summary
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

def job():
    print(f"Running job at {datetime.now()}")
    headlines = get_football_news(NEWS_API_KEY)
    if not headlines:
        print("No headlines fetched, using fallback.")
        headlines = [
            "Liverpool wins Premier League title",
            "Injury concerns for Liverpool star",
            "Spurs wins uel"
        ]
    analyzed_headlines, summary = analyze_sentiment(headlines)
    send_email(analyzed_headlines, summary)

# Run once for testing
if __name__ == "__main__":
    job()

# Schedule daily at 8 AM
# schedule.every().day.at("08:00").do(job)
# if __name__ == "__main__":
#     print("Starting football news aggregator...")
#     while True:
#         schedule.run_pending()
#         time.sleep(60)
