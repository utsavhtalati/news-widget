from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

# Base URL for Finviz
finviz_url = 'https://finviz.com/quote.ashx?t='
tickers = ['AMZN', 'AMD', 'MSTR']

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

    # Debugging: Limit to one ticker for now
    break

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

# Print the parsed data
print(parsed_data)
