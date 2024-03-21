import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import gc
import matplotlib.pyplot as plt

def modified_optimized_backtest_arbitrage_strategy(mean_n, merged_data, threshold, rolling_mean_window, dump_file_directory):
    # Convert 'timestamp' to datetime format if not already done
    if not pd.api.types.is_datetime64_any_dtype(merged_data['timestamp']):
        merged_data['timestamp'] = pd.to_datetime(merged_data['timestamp'])

    # Pre-calculate rolling statistics for efficiency
    rolling_mean = merged_data['spread'].rolling(window=mean_n).mean().values
    # rolling_std = merged_data['spread'].rolling(window=mean_n).std().values
    upper_bound = rolling_mean + threshold
    lower_bound = rolling_mean - threshold

    # Initialize numpy arrays for efficiency
    signal_start_times = np.empty(0, dtype='datetime64[ns]')
    signal_end_times = np.empty(0, dtype='datetime64[ns]')
    signal_durations = np.empty(0, dtype=int)
    timestamps = merged_data['timestamp'].values
    spreads = merged_data['spread'].values

    in_signal = False
    signal_start_index = None

    for i in tqdm(range(len(merged_data))):
        if i < mean_n - 1:  # Skip the initial window where rolling stats aren't available
            continue

        # Check if current spread crosses the bounds
        if not in_signal and (spreads[i] > upper_bound[i] or spreads[i] < lower_bound[i]):
            in_signal = True
            signal_start_index = i
        elif in_signal:
            # If in a signal, check if it continues or a new one starts within the same second
            if (spreads[i] <= upper_bound[i] and spreads[i] >= lower_bound[i]) or (spreads[i] > upper_bound[i] or spreads[i] < lower_bound[i]):
                in_signal = False
                signal_start_times = np.append(signal_start_times, timestamps[signal_start_index])
                signal_end_times = np.append(signal_end_times, timestamps[i])
                duration = (timestamps[i] - timestamps[signal_start_index]).astype('timedelta64[s]').astype(float)
                duration = 0.5 if duration < 1 else duration  # Mark durations within 1 second as 0.5
                signal_durations = np.append(signal_durations, duration)
                if spreads[i] > upper_bound[i] or spreads[i] < lower_bound[i]:
                    # If a new signal starts at the current timestamp, update the start index
                    in_signal = True
                    signal_start_index = i

    # Handle the case where a signal is still active at the end
    if in_signal:
        signal_start_times = np.append(signal_start_times, timestamps[signal_start_index])
        signal_end_times = np.append(signal_end_times, timestamps[-1])
        duration = np.maximum((timestamps[-1] - timestamps[signal_start_index]).astype('timedelta64[s]').astype(int), 1)  # Ensure minimum duration of 1s
        signal_durations = np.append(signal_durations, duration)

    # Ensure the directory exists
    check_create_directory(dump_file_directory)
    
    # Define the file path with a specific file name
    output_file_path = os.path.join(dump_file_directory, f"signal_durations_{rolling_mean_window}.csv")
    
    # Convert signal start and end times to a DataFrame
    signals_df = pd.DataFrame({'Start': signal_start_times, 'End': signal_end_times, 'Duration': signal_durations})
    
    # Save to a CSV file with the specified path
    signals_df.to_csv(output_file_path, index=False)

    # Force garbage collection
    gc.collect()

    # Calculate statistics for signal durations
    metrics = calculate_trade_durations_statistics(signal_durations, rolling_mean_window, threshold)

    # Analyze statistics
    analyze_trade_durations(signal_durations)

    return metrics

def calculate_trade_durations_statistics(trade_durations, rolling_mean_window, threshold):
    # Calculating statistics
    mean_duration = np.mean(trade_durations)
    median_duration = np.median(trade_durations)
    std_duration = np.std(trade_durations)
    max_duration = np.max(trade_durations)
    min_duration = np.min(trade_durations)

    # Count trades within specific duration intervals
    trades_within_1_sec = np.sum(trade_durations == 0.5)
    trades_1_sec = np.sum(trade_durations == 1)
    trades_2_to_5_secs = np.sum((trade_durations >= 2) & (trade_durations <= 5))
    trades_within_10_secs = np.sum(trade_durations <= 10)
    
    return {
        'Rolling Mean Window': rolling_mean_window,
        'Spread Threshold': threshold,
        'Trade Count': len(trade_durations),
        'Mean Duration (seconds)': mean_duration,
        'Median Duration (seconds)': median_duration,
        'Standard Deviation': std_duration,
        'Max Duration (seconds)': max_duration,
        'Min Duration (seconds)': min_duration,
        'Trades whithin 1 sec': trades_within_1_sec,
        'Trades in 1 sec': trades_1_sec,
        'Trades in 2-5 secs': trades_2_to_5_secs,
        'Trades within 10 secs': trades_within_10_secs
    }

def analyze_trade_durations(trade_durations):
    # Plot histogram
    plt.figure(figsize=(10, 6))
    counts, bins, patches = plt.hist(trade_durations, bins='auto', color='skyblue', alpha=0.7, rwidth=0.85)
    
    # Annotate histogram bars
    for patch in patches:
        height = patch.get_height()
        plt.annotate(f'{int(height)}', xy=(patch.get_x() + patch.get_width() / 2, height), 
                     xytext=(0, 5), textcoords='offset points', ha='center', va='bottom')
    
    plt.title('Histogram of Trade Durations')
    plt.xlabel('Duration (seconds)')
    plt.ylabel('Number of Trades')
    plt.show()