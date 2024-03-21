import pandas as pd
import os
import glob
import gc  # Garbage collection module

def calculate_spread(merged_directory, spot_name, future_name, dumping_directory):
    
    file_pattern = f"{spot_name}-{future_name}-????-??.csv" # pattern to match CSV files

    # Initialize an empty list to store all tuples
    all_spreads = [] # Will temporarily hold all spread data until written to CSV

    # Construct the full pattern for glob
    full_pattern = os.path.join(merged_directory, file_pattern)

    # Use glob to get a list of csv files based on the pattern
    csv_files = glob.glob(full_pattern)

    # Loop through each file, read it, calculate the spread, and append tuples to the list
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        print(f"Processing: {csv_file}")
        
        # Ensure 'timestamp' is in the correct datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate the spread and create a list of tuples for the current file
        # (future - spot) / spot
        file_spreads = [(row['timestamp'], (row['weighted_avg_price_future'] - row['weighted_avg_price_spot'])/row['weighted_avg_price_spot']) for index, row in df.iterrows()]
        
        # Extend the main list with the tuples from the current file
        all_spreads.extend(file_spreads)

        # Delete the DataFrame and manually trigger garbage collection
        del df
        gc.collect()
        print(f"Deleted: {csv_file}")

    # Store tuples by timestamp
    sorted_spreads = sorted(all_spreads, key=lambda x: x[0])
    print(f"Sorted: Spot {spot_name}, Future {future_name}\n")

    # Convert the list of tuples to a DataFrame
    df_spreads = pd.DataFrame(sorted_spreads, columns=['timestamp', 'spread'])

    # Construct the filename based on spot and future names
    filename = os.path.join(dumping_directory, f"spreads_{spot_name}_{future_name}.csv")
    
    # Write the DataFrame to a CSV file
    df_spreads.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    # After saving, delete the list and the DataFrame to free up memory
    del all_spreads, df_spreads
    gc.collect()
    print(f"Deleted: {csv_file}\n")
    return