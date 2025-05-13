# Bitcoin Price Hourly Tracker 📊💰

## Overview
This repository maintains Bitcoin hourly price data from 2015 to present, using a combination of historical data files and daily Snowflake backups. The system fetches current data from CryptoCompare, stores it in Snowflake, and creates daily CSV backups on GitHub.

## Repository Structure 📁
- `bitcoin-tracker-workflow-template.json`: n8n workflow template
- `btc-hourly-price_2015_2025.csv`: Complete 10y historical hourly data from November 12, 2014 through May 13, 2025
- `btc_last_YYYY-MM-DD.csv`: Daily backups of the most recent 24 hours fetched from Snowflake
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
3. Backed up daily to this repository as `btc_last_YYYY-MM-DD.csv` files

This approach provides both a complete historical record and daily snapshots of recent price movements.

## Setup Instructions 🛠️

### Prerequisites
- Snowflake account
- GitHub account and personal access token with repo permissions
- n8n instance
- CryptoCompare API key (register at [CryptoCompare](https://min-api.cryptocompare.com/))
- Optional: Telegram bot for notifications

### Step 1: Snowflake Setup
1. Log in to your Snowflake account and execute this SQL to create the database and table:

```sql
CREATE DATABASE IF NOT EXISTS BITCOIN_DATA;
USE DATABASE BITCOIN_DATA;
CREATE SCHEMA IF NOT EXISTS PRICES;
USE SCHEMA PRICES;

CREATE TABLE IF NOT EXISTS HOURLY_PRICES (
    TIME_UNIX INTEGER NOT NULL,
    DATE_STR DATE NOT NULL,
    HOUR_STR VARCHAR(2) NOT NULL,
    OPEN_PRICE FLOAT NOT NULL,
    HIGH_PRICE FLOAT NOT NULL,
    CLOSE_PRICE FLOAT NOT NULL,
    LOW_PRICE FLOAT NOT NULL,
    VOLUME_FROM FLOAT NOT NULL,
    VOLUME_TO FLOAT NOT NULL,
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (TIME_UNIX)
);
```

2. Create a Snowflake user for n8n:

```sql
CREATE USER N8N_SERVICE_USER
PASSWORD = 'your_secure_password'
DEFAULT_ROLE = N8N_ROLE;

CREATE ROLE N8N_ROLE;
GRANT USAGE ON DATABASE BITCOIN_DATA TO ROLE N8N_ROLE;
GRANT USAGE ON SCHEMA BITCOIN_DATA.PRICES TO ROLE N8N_ROLE;
GRANT SELECT, INSERT, UPDATE ON TABLE BITCOIN_DATA.PRICES.HOURLY_PRICES TO ROLE N8N_ROLE;
GRANT ROLE N8N_ROLE TO USER N8N_SERVICE_USER;
```

### Step 2: n8n Workflow Setup

1. **Import the workflow template**:
   - Open your n8n instance
   - Go to "Workflows" → "Import from file"
   - Upload the `bitcoin-tracker-workflow-template.json` file

2. **Configure Credentials**:
   - **Snowflake**: Add your Snowflake credentials
     - Account: `your-account.snowflakecomputing.com`
     - Database: `BITCOIN_DATA`
     - Schema: `PRICES`
     - Username: `N8N_SERVICE_USER`
     - Password: Your password from step 1
     - Warehouse: Your warehouse name

   - **GitHub**: Add your GitHub credentials
     - Create a Personal Access Token with repo permissions
     - Add this token to n8n

   - **Telegram** (optional): 
     - Create a Telegram bot via BotFather
     - Obtain your bot token
     - Add to n8n credentials

3. **Customize the Workflow**:
   - Edit the `Config Settings` node to set:
     - `GITHUB_USERNAME`: Your GitHub username
     - `GITHUB_REPO`: Your repository name
   
   - Edit the `Fetch Bitcoin Data` node:
     - Replace `YOUR_CRYPTOCOMPARE_API_KEY` with your actual API key
   
   - If using Telegram notifications:
     - Set `YOUR_TELEGRAM_CHAT_ID` in both Telegram nodes with your chat ID

4. **Schedule the Workflow**:
   - The template includes two triggers:
     - `Hourly Price Update Trigger`: Runs 45 minutes past each hour
     - `Daily Backup Trigger`: Runs at 23:55 daily
   - Adjust these schedules if needed

5. **Activate the Workflow**:
   - Once configured, toggle the "Active" switch to enable the workflow

### Step 3: Initial Data Load

1. Download the historical Bitcoin data from January 1, 2015 to May 13, 2025:
   - Use the CryptoCompare API with the Historical Hour Data endpoint
   - Or use a provided CSV if available in this repository

2. Upload this historical data to your GitHub repository as `btc-hourly-price_2015_2025.csv`

3. Wait for the workflow to run automatically or trigger it manually to start collecting new data

## Usage 📊

### Accessing Historical Data
The complete historical dataset from 2015-2025 is available in the `btc-hourly-price_2015_2025.csv` file. This contains all hourly OHLCV data for the entire period.

### Accessing Recent Data
Daily snapshots of the most recent 24 hours are available in files named `btc_last_YYYY-MM-DD.csv`. Each file contains exactly 24 hours of data.

### Querying Snowflake Data
You can use SQL to query the historical data in Snowflake:

```sql
-- Get all data for a specific date
SELECT * FROM BITCOIN_DATA.PRICES.HOURLY_PRICES
WHERE DATE_STR = '2025-05-13'
ORDER BY TIME_UNIX;

-- Get daily average prices for the past month
SELECT 
  DATE_STR,
  AVG(OPEN_PRICE) AS avg_open,
  AVG(CLOSE_PRICE) AS avg_close,
  MAX(HIGH_PRICE) AS highest,
  MIN(LOW_PRICE) AS lowest,
  SUM(VOLUME_FROM) AS total_volume_btc
FROM BITCOIN_DATA.PRICES.HOURLY_PRICES
WHERE DATE_STR >= DATEADD(month, -1, CURRENT_DATE())
GROUP BY DATE_STR
ORDER BY DATE_STR;
```

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

### Adding More Cryptocurrencies
To track additional cryptocurrencies:
1. Create new tables in Snowflake for each cryptocurrency
2. Clone and modify the workflow, changing the API parameters
3. Update the file naming convention to distinguish between cryptocurrencies

## License 📄
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏
- CryptoCompare for providing the Bitcoin price API
- n8n for the workflow automation platform
- Snowflake for the data warehousing solution
- GitHub for version control and file storage
