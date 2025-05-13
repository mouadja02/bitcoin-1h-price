import os
import pandas as pd
import glob
from datetime import datetime

def consolidate_bitcoin_data(historical_file, daily_files_pattern, output_file):
    """
    Consolidate historical Bitcoin data with daily updates into a single CSV file
    
    Args:
        historical_file (str): Path to historical data CSV file
        daily_files_pattern (str): Glob pattern to match daily update files
        output_file (str): Path to write the consolidated output file
    """
    print(f"Reading historical data from {historical_file}...")
    
    # Read historical data
    try:
        historical_df = pd.read_csv(historical_file)
        print(f"  - Found {len(historical_df)} historical records")
    except Exception as e:
        print(f"Error reading historical file: {e}")
        return
    
    # Convert TIME_UNIX to numeric to ensure proper sorting
    historical_df['TIME_UNIX'] = pd.to_numeric(historical_df['TIME_UNIX'])
    
    # Find all daily update files
    daily_files = sorted(glob.glob(daily_files_pattern))
    print(f"Found {len(daily_files)} daily update files")
    
    # Create a set of existing timestamps for faster duplicate checking
    existing_timestamps = set(historical_df['TIME_UNIX'].values)
    
    # Process each daily file
    all_new_records = []
    for file in daily_files:
        try:
            daily_df = pd.read_csv(file)
            
            # Convert TIME_UNIX to numeric
            daily_df['TIME_UNIX'] = pd.to_numeric(daily_df['TIME_UNIX'])
            
            # Filter out records that already exist in the historical data
            new_records = daily_df[~daily_df['TIME_UNIX'].isin(existing_timestamps)]
            
            if len(new_records) > 0:
                print(f"  - {os.path.basename(file)}: Adding {len(new_records)} new records")
                all_new_records.append(new_records)
                
                # Update the set of existing timestamps
                existing_timestamps.update(new_records['TIME_UNIX'].values)
            else:
                print(f"  - {os.path.basename(file)}: No new records")
                
        except Exception as e:
            print(f"  - Error processing {file}: {e}")
    
    # Combine all new records
    if all_new_records:
        new_records_df = pd.concat(all_new_records, ignore_index=True)
        print(f"Total new records: {len(new_records_df)}")
        
        # Combine with historical data
        combined_df = pd.concat([historical_df, new_records_df], ignore_index=True)
        
        # Sort by timestamp
        combined_df = combined_df.sort_values('TIME_UNIX')
        
        # Remove any duplicates that might have slipped through
        combined_df = combined_df.drop_duplicates(subset=['TIME_UNIX'])
        
        print(f"Writing consolidated data to {output_file} ({len(combined_df)} total records)...")
        combined_df.to_csv(output_file, index=False)
        print("Done!")
    else:
        print("No new records found. Historical data is already up-to-date.")
        # Copy the historical file to output file
        historical_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    # Configure these paths according to your repository structure
    HISTORICAL_FILE = "btc-hourly-price_2020_2025.csv"
    DAILY_FILES_PATTERN = "btc_last24h_*.csv"
    OUTPUT_FILE = f"btc-hourly-price_consolidated_{datetime.now().strftime('%Y%m%d')}.csv"
    
    consolidate_bitcoin_data(HISTORICAL_FILE, DAILY_FILES_PATTERN, OUTPUT_FILE)
