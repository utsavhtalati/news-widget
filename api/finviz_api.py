from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import time

# Function to fetch news and calculate sentiment for a list of tickers
def fetch_sentiment_for_tickers(tickers):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    news_tables = {}
    parsed_data = []

    # Fetch news tables for each ticker
    for ticker in tickers:
        try:
            url = finviz_url + ticker
            req = Request(url=url, headers={'User-Agent': 'my-app'})
            response = urlopen(req)

            html = BeautifulSoup(response, 'html.parser')
            news_table = html.find(id='news-table')
            news_tables[ticker] = news_table

            # Parse news titles and dates
            if news_table:
                for row in news_table.findAll('tr'):
                    try:
                        # Extract news title and date/time
                        link_tag = row.find('a')
                        if not link_tag:
                            continue
                        title = link_tag.text.strip()
                        date_data = row.td.text.strip().split(' ')
                        if len(date_data) == 1:
                            news_time = date_data[0]  # Rename to avoid shadowing the `time` module
                            date = None
                        else:
                            date = date_data[0]
                            news_time = date_data[1]

                        parsed_data.append([ticker, date, news_time, title])
                    except AttributeError:
                        continue
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

        # Delay to avoid being rate-limited
        time.sleep(1)

    # Create a DataFrame
    df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])

    # Sentiment Analysis
    vader = SentimentIntensityAnalyzer()
    df['compound'] = df['title'].apply(lambda title: vader.polarity_scores(title)['compound'])

    # Group by ticker and calculate mean sentiment
    sentiment_df = df.groupby('ticker')['compound'].mean().reset_index()
    return sentiment_df

# Function to process stocks in batches
def process_stocks_in_batches(all_tickers, batch_size=10, sentiment_threshold=0.5):
    high_sentiment_stocks = []

    # Process tickers in batches
    for i in range(0, len(all_tickers), batch_size):
        batch = all_tickers[i:i+batch_size]
        sentiment_df = fetch_sentiment_for_tickers(batch)

        # Filter stocks with sentiment above the threshold
        filtered_df = sentiment_df[sentiment_df['compound'] > sentiment_threshold]
        high_sentiment_stocks.append(filtered_df)

    # Combine results from all batches
    result_df = pd.concat(high_sentiment_stocks, ignore_index=True)
    return result_df

# List of stocks to analyze (replace this with your list or an API call to fetch tickers)
all_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NFLX', 'META', 'NVDA', 'INTC', 'AMD', 'RCL', 'CCL', 'NCLH']

# Analyze stocks in batches and find those with high sentiment
high_sentiment_stocks = process_stocks_in_batches(all_tickers, batch_size=5, sentiment_threshold=0.2)

# Display the results
print("Stocks with High Sentiment:")
print(high_sentiment_stocks)

# Save results to a CSV file
high_sentiment_stocks.to_csv("high_sentiment_stocks.csv", index=False)