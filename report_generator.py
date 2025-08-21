def generate_daily_signal_report(csv_file):
    import pandas as pd
    df = pd.read_csv(csv_file)
    summary = df.groupby("signal").size()
    print("?YZ G1?4nl1?4k Sinyal Da"Y"+/-l"+/-m"+/-:\n", summary)
