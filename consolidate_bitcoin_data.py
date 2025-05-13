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
            # Try to read the file with different parsing options
            # to handle potential formatting issues
            try:
                # First try with standard reading
                daily_df = pd.read_csv(file)
            except:
                # If that fails, try with flexible whitespace handling
                daily_df = pd.read_csv(file, skipinitialspace=True)
                
            # Clean up column names (remove any leading/trailing whitespace)
            daily_df.columns = daily_df.columns.str.strip()
            
            # Debug: print column names
            print(f"Columns in {file}: {daily_df.columns.tolist()}")
            
            # Debug: print first few rows
            print(f"First 2 rows from {file}:")
            print(daily_df.head(2))
            
            # Ensure TIME_UNIX is treated as numeric
            daily_df['TIME_UNIX'] = pd.to_numeric(daily_df['TIME_UNIX'], errors='coerce')
            daily_df = daily_df.dropna(subset=['TIME_UNIX'])
            
            # Convert TIME_UNIX to integers to match the historical data
            daily_df['TIME_UNIX'] = daily_df['TIME_UNIX'].astype(int)
            
            # Filter out records that already exist in the historical data
            new_records_df = daily_df[~daily_df['TIME_UNIX'].isin(existing_timestamps)]
            
            if len(new_records_df) > 0:
                new_records.append(new_records_df)
                # Update the set of existing timestamps
                existing_timestamps.update(new_records_df['TIME_UNIX'].values)
                print(f"Added {len(new_records_df)} new records from {os.path.basename(file)}")
            else:
                print(f"No new records in {os.path.basename(file)} after filtering")
                
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

def check_file_content(file_path):
    """
    Debug function to examine file content directly
    """
    try:
        with open(file_path, 'r') as f:
            print(f"First 5 lines of {file_path}:")
            for i in range(5):
                line = f.readline().strip()
                print(f"Line {i+1}: {line}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    # Check if the files exist first
    historical_file = "btc-hourly-price_2015_2025.csv"
    pattern = "btc_ohclv_*.csv"
    
    if not os.path.exists(historical_file):
        print(f"Warning: Historical file '{historical_file}' not found!")
    
    daily_files = glob.glob(pattern)
    if not daily_files:
        print(f"Warning: No files matching pattern '{pattern}' found!")
    else:
        for file in daily_files:
            check_file_content(file)
    
    # Run the consolidation
    consolidate_bitcoin_data(
        historical_file=historical_file,
        daily_backups_pattern=pattern,
        output_file="btc-hourly-price_consolidated.csv"
    )
