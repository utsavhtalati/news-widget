from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt

# Base URL for Finviz
finviz_url = 'https://finviz.com/quote.ashx?t='
tickers = ['RCL', 'CCL', 'NCLH']

news_tables = {}

# Fetch and parse the news table for each ticker
for ticker in tickers:
    url = finviz_url + ticker

    # Request the page
    req = Request(url=url, headers={'User-Agent': 'my-app'})
    response = urlopen(req)

    # Parse the HTML response with BeautifulSoup
    html = BeautifulSoup(response, 'html.parser')  # Explicitly specify the parser

    # Find the news table by ID
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

parsed_data = []

# Process the extracted news tables
for ticker, news_table in news_tables.items():
    if news_table:  # Ensure the table exists
        for row in news_table.findAll('tr'):
            try:
                # Get the <a> tag and its text
                link_tag = row.find('a')
                if not link_tag:  # Skip rows without a title link
                    continue
                title = link_tag.text.strip()  # Strip extra whitespace

                # Extract the date and time
                date_data = row.td.text.strip().split(' ')  # Clean and split date/time
                if len(date_data) == 1:
                    time = date_data[0]
                    date = None  # If only time is available
                else:
                    date = date_data[0]
                    time = date_data[1]

                # Append the parsed data
                parsed_data.append([ticker, date, time, title])
            except AttributeError:
                # Safely skip rows missing required elements
                continue

# Create a DataFrame
df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])

# Sentiment Analysis
vader = SentimentIntensityAnalyzer()
df['compound'] = df['title'].apply(lambda title: vader.polarity_scores(title)['compound'])

# Convert `date` column to datetime and drop invalid rows
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
df = df.dropna(subset=['date'])  # Remove rows where `date` is NaT (invalid date)

# Group by ticker and date, and calculate the mean compound sentiment
mean_df = df.groupby(['ticker', 'date'])[['compound']].mean().reset_index()

# Pivot the DataFrame for plotting
pivot_df = mean_df.pivot(index='date', columns='ticker', values='compound')

# Plot the results
pivot_df.plot(kind='bar', figsize=(14, 8), legend=True, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
plt.title("Mean Sentiment Scores Over Time by Stock", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Mean Sentiment (Compound Score)", fontsize=12)
plt.xticks(rotation=45, fontsize=10)
plt.legend(title="Ticker", fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Annotate highest and lowest points
for ticker in pivot_df.columns:
    for date, value in pivot_df[ticker].dropna().items():
        plt.text(pivot_df.index.get_loc(date), value, f'{value:.2f}', ha='center', va='bottom' if value > 0 else 'top')

plt.show()
