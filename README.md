# Bitcoin Price History Tracker

## Overview
This repository contains an automated system for tracking, storing, and backing up Bitcoin hourly price data using Snowflake and n8n. The system fetches data from CryptoCompare, maintains a complete history in Snowflake, and creates daily CSV backups on GitHub.

## Features
- **Real-time Data Collection**: Automatically fetches hourly Bitcoin OHLCV data
- **Comprehensive Storage**: Maintains full historical price data in Snowflake
- **Daily Backups**: Creates daily CSV backups of the most recent 24 hours
- **Automated Workflows**: Uses n8n for reliable automation of all tasks
- **Data Integrity**: Ensures no gaps in historical price data

## Data Structure
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

## Repository Structure
- `/daily_backups`: Daily CSV backups of the most recent 24 hours of price data
- `/scripts`: Helper scripts for data processing
- `/docs`: Documentation and setup guides

## Setup Instructions

### Prerequisites
- Snowflake account
- GitHub account
- n8n instance
- CryptoCompare API key: `fb4f8e26d4a0fec6b05a9ae93d937f5697519d50a8f48d0f228901056c6d4bf5`

### Snowflake Setup
1. Create the database and tables:
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

2. Create a user for n8n:
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

### n8n Workflow Setup
1. Import the workflow JSON files into your n8n instance
2. Configure Snowflake credentials:
   - Host: your-account.snowflakecomputing.com
   - Database: BITCOIN_DATA
   - Schema: PRICES
   - Username: N8N_SERVICE_USER
   - Password: [your password]
   - Warehouse: [your warehouse]

3. Configure GitHub credentials:
   - Add a Personal Access Token with repo permissions

4. Activate the workflows:
   - Hourly Data Collection: Runs every hour to fetch latest data
   - Daily Backup: Runs at midnight to create GitHub CSV backups

## Usage

### Querying Historical Data
You can query the historical data in Snowflake:

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

### Accessing Backup Files
Daily backup files are stored in the `/daily_backups` folder with filenames in the format `btc_last24h_YYYY-MM-DD.csv`.

## Maintenance

### Adding More Cryptocurrencies
To add more cryptocurrencies, create additional tables in Snowflake and modify the workflows to fetch data for those cryptocurrencies.

### Handling API Rate Limits
The CryptoCompare API has rate limits. The current key allows for up to 250,000 API calls per month, which is sufficient for the current setup.

## Troubleshooting

### Common Issues
- **"No data returned from Snowflake"**: Check your Snowflake connection and query.
- **GitHub backup fails**: Verify your GitHub credentials and repository permissions.
- **Missing data points**: Run the gap detection workflow to identify and fill missing hours.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- CryptoCompare for providing the Bitcoin price API
- n8n for the workflow automation platform
- Snowflake for the data warehousing solution
