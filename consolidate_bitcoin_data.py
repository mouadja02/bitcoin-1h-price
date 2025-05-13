import os
import pandas as pd
import glob
from datetime import datetime

def consolidate_bitcoin_data(historical_file, daily_backups_pattern, output_file):
    """
    Consolidate historical Bitcoin data with daily backup files.
    
    Args:
        historical_file: Path to the main historical data file
        daily_backups_pattern: Glob pattern to match daily backup files
        output_file: Path where the consolidated CSV will be saved
    """
    print(f"Reading historical data from {historical_file}...")
    
    # Read the historical data file
    try:
        historical_df = pd.read_csv(historical_file)
        print(f"Loaded {len(historical_df)} historical records.")
    except Exception as e:
        print(f"Error reading historical file: {e}")
        return
    
    # Create a set of existing timestamps for quick lookup
    existing_timestamps = set(historical_df['TIME_UNIX'].values)
    
    # Get all daily backup files and sort them by name
    daily_files = sorted(glob.glob(daily_backups_pattern))
    print(f"Found {len(daily_files)} daily backup files.")
    
    # Process each daily file
    new_records = []
    for file in daily_files:
        try:
            daily_df = pd.read_csv(file)
            
            # Filter out records that already exist in the historical data
            new_records_df = daily_df[~daily_df['TIME_UNIX'].isin(existing_timestamps)]
            
            if len(new_records_df) > 0:
                new_records.append(new_records_df)
                # Update the set of existing timestamps
                existing_timestamps.update(new_records_df['TIME_UNIX'].values)
                print(f"Added {len(new_records_df)} new records from {os.path.basename(file)}")
            else:
                print(f"No new records in {os.path.basename(file)}")
                
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    # If we found new records, combine them with the historical data
    if new_records:
        # Concatenate all new records
        new_records_df = pd.concat(new_records, ignore_index=True)
        
        # Combine with historical data
        combined_df = pd.concat([historical_df, new_records_df], ignore_index=True)
        
        # Sort by timestamp to ensure chronological order
        combined_df = combined_df.sort_values(by='TIME_UNIX')
        
        # Save the consolidated data
        combined_df.to_csv(output_file, index=False)
        print(f"Saved consolidated data with {len(combined_df)} records to {output_file}")
        print(f"Added a total of {len(combined_df) - len(historical_df)} new records")
        
        # Print the date range
        start_date = datetime.fromtimestamp(combined_df['TIME_UNIX'].min()).strftime('%Y-%m-%d %H:%M:%S')
        end_date = datetime.fromtimestamp(combined_df['TIME_UNIX'].max()).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Data ranges from {start_date} to {end_date}")
    else:
        print("No new records found in daily backup files.")

if __name__ == "__main__":
    # Usage example
    consolidate_bitcoin_data(
        historical_file="btc-hourly-price_2015_2025.csv",
        daily_backups_pattern="btc_last_*.csv",
        output_file="btc-hourly-price_consolidated.csv"
    )
