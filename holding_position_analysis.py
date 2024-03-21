import pandas as pd
import numpy as np
from tqdm import tqdm  # Import tqdm for progress bar functionality
import gc  # Garbage collection module
import matplotlib.pyplot as plt

def backtest_arbitrage_strategy_hedging_ratio_version_rolling(mean_n, merged_data, threshold, rolling_mean_window):
    # Ensure 'timestamp' is in datetime format
    merged_data['timestamp'] = pd.to_datetime(merged_data['timestamp'])

    trade_entry_times = []  # Stores the entry time for each trade
    trade_exit_times = []  # Stores the exit time for each trade
    trade_count = 0
    # spread_ratio_every = []
    previous_position = None # Future
    previous_entry_time = None  # Track the entry time for the current position
    
    for i, row in tqdm(merged_data.iterrows(), total=merged_data.shape[0]):
        if i>1*60*60*24*7:
            spread_ratio = row['spread']
            mean_min=merged_data['spread'].iloc[i-mean_n:i].mean() #过去3min作为mean
            current_time = row['timestamp']
            if not previous_position:
                if spread_ratio > threshold + mean_min:
                    previous_position = 'short' # enter short in future & long in spot   merged_data['future_close'] - merged_data['spot_close']
                    trade_count += 1

                    previous_entry_time = current_time # record time
                    # spread_ratio_every.append(spread_ratio)
                    
                elif spread_ratio < -threshold+mean_min:
                    previous_position = 'long' # enter long in future & short in spot
                    trade_count += 1

                    previous_entry_time = current_time # record time
                    # spread_ratio_every.append(spread_ratio)

            else:
                if previous_position == 'short' and spread_ratio < -threshold + mean_min:
                    # exit short in future & long in spot
                    trade_exit_times.append(current_time)
                    trade_entry_times.append(previous_entry_time)
                        
                    # enter long in future & short in spot
                    previous_position = 'long' # long future, short spot
                    trade_count += 1
                    
                    previous_entry_time = current_time
                    # spread_ratio_every.append(spread_ratio)
                        
                elif previous_position == 'long' and spread_ratio > threshold+mean_min:
                    # exit long in future & short in spot
                    trade_exit_times.append(current_time)
                    trade_entry_times.append(previous_entry_time)
                        
                    # enter long in future & short in spot
                    previous_position = 'short' # short future, long spot
                    trade_count += 1
                    
                    previous_entry_time = current_time
                    # spread_ratio_every.append(spread_ratio)

    del merged_data  # merged_data is no longer needed
    gc.collect()

    trade_durations = [(exit_time - entry_time).total_seconds() for entry_time, exit_time in zip(trade_entry_times, trade_exit_times)]
    average_trade_duration = sum(trade_durations) / len(trade_durations) if trade_durations else 0

    metrics = {
        'Rolling Mean Window': rolling_mean_window,
        'Spread Threshold': threshold,
        'Trade Count': len(trade_entry_times),  # counting the actual number of trades
        'Average Trade Duration (seconds)': average_trade_duration,
    }

    # Analyze statistics
    analyze_trade_durations(trade_durations)

    del trade_durations, trade_entry_times, trade_exit_times
    gc.collect()

    return metrics#, trade_count, spread_ratio_every


def analyze_trade_durations(trade_durations):
    # Calculate statistics
    durations_array = np.array(trade_durations)
    mean_duration = np.mean(durations_array)
    median_duration = np.median(durations_array)
    std_duration = np.std(durations_array)
    max_duration = np.max(durations_array)
    min_duration = np.min(durations_array)
    
    # Print statistics
    print(f"Mean Trade Duration: {mean_duration} seconds")
    print(f"Median Trade Duration: {median_duration} seconds")
    print(f"Standard Deviation of Trade Durations: {std_duration}")
    print(f"Max Trade Duration: {max_duration} seconds")
    print(f"Min Trade Duration: {min_duration} seconds")
    
    # Plot histogram
    plt.figure(figsize=(10, 6))
    counts, bins, patches = plt.hist(durations_array, bins='auto', color='blue', alpha=0.7, rwidth=0.85)
    
    # Annotate histogram bars
    for count, bin, patch in zip(counts, bins, patches):
        height = patch.get_height()
        plt.annotate(f'{int(count)}', xy=(bin, height), xytext=(0, 5), textcoords='offset points', ha='center', va='bottom')
    
    plt.title('Histogram of Trade Durations')
    plt.xlabel('Duration (seconds)')
    plt.ylabel('Number of Trades')
    plt.show()