# Bitcoin Price Hourly Tracker 📊💰

## Overview
This repository maintains Bitcoin hourly price data from 2015 to present, using a combination of historical data files and daily Snowflake backups. The system fetches current data from CryptoCompare, stores it in Snowflake, and creates daily CSV backups on GitHub.

## Repository Structure 📁
- `btc-hourly-price_2015_2025.csv`: Complete 10y historical hourly data from November 12, 2014 through May 13, 2025
- `btc_ohclv_YYYY-MM-DD.csv`: Daily backups of the most recent 24 hours fetched from Snowflake
- `README.md`: This documentation file

## Data Structure 📈
Bitcoin price data is stored with the following schema:

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| TIME_UNIX   | INTEGER   | Unix timestamp for the hourly data point |
| DATE_STR    | DATE      | Date in YYYY-MM-DD format |
| HOUR_STR    | VARCHAR   | Hour in 24-hour format (00-23) |
| OPEN_PRICE  | FLOAT     | Opening price for the hour |
| HIGH_PRICE  | FLOAT     | Highest price during the hour |
| CLOSE_PRICE | FLOAT     | Closing price for the hour |
| LOW_PRICE   | FLOAT     | Lowest price during the hour |
| VOLUME_FROM | FLOAT     | Volume in BTC |
| VOLUME_TO   | FLOAT     | Volume in USD |

## Data License and Use 📋
This dataset is free to use and is specifically designed for machine learning projects and research purposes. You're welcome to use this data for academic research, training ML models, educational purposes, and non-commercial applications. Attribution is appreciated but not required.

## Data Sources and Workflow ⚙️

### Historical Data 🗄️
The `btc-hourly-price_2015_2025.csv` file contains the complete historical record of Bitcoin hourly prices from January 1, 2015 through May 13, 2025. This serves as the foundational dataset and remains static.

### Daily Updates 🔄
New hourly data is:
1. Collected from CryptoCompare API
2. Stored in Snowflake database ❄️
3. Backed up daily to this repository as `btc_ohclv_YYYY-MM-DD.csv` files

This approach provides both a complete historical record and daily snapshots of recent price movements.

## Usage 📊

### Accessing Historical Data
The complete historical dataset from 2015-2025 is available in the `btc-hourly-price_2015_2025.csv` file. This contains all hourly OHLCV data for the entire period.

### Accessing Recent Data
Daily snapshots of the most recent 24 hours are available in files named `btc_ohclv_YYYY-MM-DD.csv`. Each file contains exactly 24 hours of data.

## Future Plans: Consolidated Historical Data 🔮

In a future update, I plan to develop functionality to merge the new daily updates with the historical data to maintain a single comprehensive CSV file. Currently, this is challenging because:

1. The historical data file contains over 90,000 lines
2. Appending data requires reading the entire file and adding content at the end
3. Managing this process within GitHub's file size limits requires careful handling

### Consolidation Script

In the meantime, you can use 'consolidate_bitcoin_data.py' Python script to combine all data files into a single up-to-date CSV. Run it in the repository directory to create an up-to-date consolidated CSV file containing all historical and new data in chronological order.

## Troubleshooting 🔍

### Common Issues

- **"No data returned from Snowflake"**: 
  - Check your Snowflake connection credentials
  - Verify that your database, schema, and table names match exactly
  - Ensure your Snowflake user has appropriate permissions

- **GitHub backup fails**: 
  - Verify your GitHub credentials and repository permissions
  - Check that your Personal Access Token hasn't expired
  - Ensure your repository exists and is accessible

- **API calls failing**:
  - Verify your CryptoCompare API key is valid
  - Check if you've hit API rate limits (free tier: 10,000 calls per month)
  - Try reducing the frequency of calls if needed

- **Missing Telegram notifications**:
  - Ensure your bot token is valid
  - Check that your bot is a member of the specified chat
  - Verify the chat ID is correct

## Maintenance 🔧

### API Rate Limits
The CryptoCompare API has rate limits: 11,000 calls per month
- This workflow uses approximately 750 calls per month (hourly fetching)

## License 📄
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏
- CryptoCompare for providing the Bitcoin price API
- n8n for the workflow automation platform
- Snowflake for the data warehousing solution
- GitHub for version control and file storage
