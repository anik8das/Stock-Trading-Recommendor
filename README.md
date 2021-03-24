# Stock-Trading-Recommendor
A Python program to suggest Stocks for Value Investing, Call Options trading, and Put Options trading. Recommendors are implemented as classes, and the specific criteria can be modified through parameters passed to the constructor.

### Libraries used
1. yfinance for stock data, history, and properties
2. pandas for dataframe operations
3. datatime for date management
4. pickle for external file handling
5. os and sys to hide unecessary output
6. numpy for statistical calculations

### Value Investing Logic
Stocks are checked for:
1. Market Cap: At least 100B 
2. Analyst Ratings: At least be an outperform on average
3. Yearly change: At least up 25% over the last year
4. Country: Chinese stocks are avoided due to unreliability
5. Dollar volume: At least 500 million
6. Suggested stocks are updated every 30 days
7. The parameters can be changed through the constructor
8. Final object is memoized in an external file to prevent needless recalculation

### Put Option Investing Logic:
Stocks are checked for:
1. An underperform analyst rating at most
2. Either an increase of at least 40% or a decrease of at least 20%
3. A decrease in speculated Price to Earnings ratio by at least 10%
4. Suggested stocks are updated every 30 days
5. The parameters can be modified through the constructor
6. Final object is memoized in an external file to prevent needless recalculation

Examples to test out the code are included at the bottom of each file. Call Option logic hasn't been finalized yet.<br>
Happy Investing!
