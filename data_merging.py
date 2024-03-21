import pandas as pd
import os

def read_and_merge_csv_files(spot_directory, future_directory, spot_names, future_names, years, months, merged_directory):
    for year in years:
        for month in months:
            for spot_name in spot_names:
                for future_name in future_names:
                    # perpare to read spot price data
                    spot_filename = f"processed_{spot_name}-aggTrades-{year}-{month:02d}.csv"
                    spot_filepath = os.path.join(spot_directory, spot_filename)

                    # perpare to read future price data
                    future_filename = f"processed_{future_name}-aggTrades-{year}-{month:02d}.csv"
                    future_filepath = os.path.join(future_directory, future_filename)

                    # read spot and future price data, and merge the future price to 
                    if os.path.exists(spot_filepath) and os.path.exists(future_filepath):
                        spot_df = pd.read_csv(spot_filepath)
                        future_df = pd.read_csv(future_filepath)
                        # convert to datetime format
                        spot_df['timestamp'] = pd.to_datetime(spot_df['timestamp'])
                        future_df['timestamp'] = pd.to_datetime(future_df['timestamp'])
                        # rename 'weighted_avg_price' column in spot_df to 'weighted_avg_price_spot'
                        # rename 'weighted_avg_price' column in future_df to 'weighted_avg_price_future'
                        spot_df = spot_df.rename(columns={'weighted_avg_price': 'weighted_avg_price_spot'})
                        future_df = future_df.rename(columns={'weighted_avg_price': 'weighted_avg_price_future'})
                        print(f"Read files: {spot_filepath} and {future_filepath}")

                        # ensure 'timestamp' is the index for the merge operation
                        spot_df.set_index('timestamp', inplace=True)
                        future_df.set_index('timestamp', inplace=True)
                        # Perform an outer merge to include all timestamps from both DataFrames
                        merged_df = pd.merge(spot_df, future_df, left_index=True, right_index=True, how='outer', sort=True)
                        # forward fill missing values in future_df columns for indices that do not match
                        merged_df.ffill(inplace=True)
                        # backward fill missing values
                        merged_df.bfill(inplace=True)
                        print(f"Merge files: {spot_filepath} and {future_filepath}")
                        # return merged_df
                    
                        # save the merged_df
                        # Construct the filename using the provided format
                        merged_filename = f"{spot_name}-{future_name}-{year}-{month:02d}.csv"
                        # Full path for the CSV file
                        merged_file_path = os.path.join(merged_directory, merged_filename)
                        # Save the DataFrame as a CSV file
                        merged_df.to_csv(merged_file_path)
                        print(f"CSV file saved: {merged_file_path}")
                    else:
                        print(f"File does not exist: {spot_filepath} or {future_filepath}")
                        return None

def read_csv_files(merged_directory, spot_names, future_names, years, months):
    for year in years:
        for month in months:
            for spot_name in spot_names:
                for future_name in future_names:
                    filename = f"{spot_name}-{future_name}-{year}-{month:02d}.csv"
                    filepath = os.path.join(merged_directory, filename)
            
                # Check if the file exists before trying to read it
                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    print(f"Read file: {filename}")
                    return df
                else:
                    print(f"File does not exist: {filename}")
                    return None