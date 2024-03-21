import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_spread_statistics(spreads_df):
    """
    Calculate and plot statistics for the 'spread' column in a DataFrame.
    
    Parameters:
    - spreads_df: DataFrame with a 'spread' column.
    
    Returns:
    - A dictionary with mean, median, standard deviation, min, and max spread statistics.
    """
    # Extract the 'spread' column
    spread_values = spreads_df['spread'].values

    # Calculate statistics
    mean_spread = np.mean(spread_values)
    median_spread = np.median(spread_values)
    std_spread = np.std(spread_values)
    min_spread = np.min(spread_values)
    max_spread = np.max(spread_values)
    two_sigma_range = (mean_spread - 2 * std_spread, mean_spread + 2 * std_spread)

    # Plotting the histogram with count annotations
    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(spread_values, bins=30, color='skyblue', alpha=0.7)
    plt.title('Histogram of Spread')
    plt.xlabel('Spread')
    plt.ylabel('Frequency')
    plt.grid(True)

    # Annotate each bar with the count
    for rect in patches:
        height = rect.get_height()
        plt.annotate(f'{int(height)}',
                     xy=(rect.get_x() + rect.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.show()

    # Prepare and return the statistics
    stats = {
        'mean_spread': mean_spread,
        'median_spread': median_spread,
        'std_spread': std_spread,
        'min_spread': min_spread,
        'max_spread': max_spread
    }

    print(f"mean_duration: {mean_spread}")
    print(f"median_duration: {median_spread}")
    print(f"std_deviation: {std_spread}")
    print(f"min_duration: {min_spread}")
    print(f"max_duration: {max_spread}")
    print(f"total_count: {len(spread_values)}")

    return stats

def compare_signal_density_by_date(input_files, labels, time_frame=None, plot_type='density'):
    plt.figure(figsize=(10, 6))  # Adjust figure size for better readability
    
    # Define a set of colors and line styles for maximum separability
    colors = sns.color_palette('bright')[:len(input_files)]  # Use a bright color palette for better separation
    
    for i, (input_file, label) in enumerate(zip(input_files, labels)):
        signals_df = pd.read_csv(input_file)
        signals_df['Start'] = pd.to_datetime(signals_df['Start'])

        if time_frame:
            start_date, end_date = pd.to_datetime(time_frame[0]), pd.to_datetime(time_frame[1])
            signals_df = signals_df[(signals_df['Start'] >= start_date) & (signals_df['Start'] <= end_date)]

        if plot_type == 'density':
            sns.kdeplot(data=signals_df['Start'], shade=True, bw_adjust=0.1, label=label, color=colors[i])
        elif plot_type == 'count':
            sns.histplot(data=signals_df['Start'], kde=False, label=label, color=colors[i], element='step')
            ## Using plt.hist for better control over annotations
            # counts, bins, _ = plt.hist(signals_df['Start'], bins=30, label=label, color=colors[i], alpha=0.75)  # Adjust `bins` as needed

            # # Annotate bars with counts over 500
            # for count, bin in zip(counts, bins):
            #     if count > 500:  # Only annotate bars with counts over 500
            #         plt.text(bin, count, f'{int(count)}', ha='center', va='bottom')
    
    plt.title(f'Comparative {"Density" if plot_type == "density" else "Count"} of Trading Signals Over Time')
    plt.xlabel('Date')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
    plt.ylabel('Density' if plot_type == 'density' else 'Count')
    plt.legend(loc='upper left')  # Move legend to the upper left or adjust as needed
    plt.tight_layout()  # Adjust layout for better fit
    plt.show()

def analyze_signal_density_by_date(input_file, time_frame=None):
    """
    Plots the density of trading signals over time.
    
    Parameters:
    - input_file: The file path to read signal durations from.
    - time_frame: An optional tuple specifying the start and end of the time frame to analyze. 
                  Format: ('YYYY-MM-DD', 'YYYY-MM-DD'). If not provided, analyzes the entire dataset.
    """
    # Read the data
    signals_df = pd.read_csv(input_file)
    
    # Convert 'Start' to datetime if not already
    signals_df['Start'] = pd.to_datetime(signals_df['Start'])

    if time_frame:
        # Assuming time_frame is a date range
        start_date, end_date = pd.to_datetime(time_frame[0]), pd.to_datetime(time_frame[1])
        signals_df = signals_df[(signals_df['Start'] >= start_date) & (signals_df['Start'] <= end_date)]
    
    # Plot density
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=signals_df['Start'], shade=True, bw_adjust=0.1)
    plt.title('Density of Trading Signals Over Time')
    plt.xlabel('Date')
    plt.ylabel('Density')
    plt.gcf().autofmt_xdate()  # Auto-format the x-axis labels for better readability
    plt.show()
