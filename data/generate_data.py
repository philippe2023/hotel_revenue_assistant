import pandas as pd
import random
from datetime import datetime, timedelta

# Generate date range for one month
start_date = datetime(2024, 1, 1)
end_date = start_date + timedelta(days=29)
date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

# Generate hotel data for testing
data = {
    "Date": [date.strftime("%Y-%m-%d") for date in date_range],
    "Your Rate": [random.randint(100, 200) for _ in date_range],
    "Competitor A Rate": [random.randint(95, 205) for _ in date_range],
    "Competitor B Rate": [random.randint(90, 195) for _ in date_range],
    "Competitor C Rate": [random.randint(85, 210) for _ in date_range],
    "Competitor D Rate": [random.randint(110, 220) for _ in date_range],
    "Competitor E Rate": [random.randint(120, 230) for _ in date_range],
    "Min LOS": [random.randint(1, 3) for _ in date_range],  # Minimum Length of Stay
    "Advance Purchase": [random.randint(7, 30) for _ in date_range],  # Advance Purchase in days
}

# Create a DataFrame
df = pd.DataFrame(data)

# Add a consolidated "Competitor Rates" column as an average of all competitors
competitor_columns = ["Competitor A Rate", "Competitor B Rate", "Competitor C Rate", "Competitor D Rate", "Competitor E Rate"]
df["Competitor Rates"] = df[competitor_columns].mean(axis=1)

# Save as a CSV file
file_path = "hotel_competitor_rates.csv"
df.to_csv(file_path, index=False)

print(f"CSV file saved at: {file_path}")