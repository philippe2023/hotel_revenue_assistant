import pandas as pd
from io import StringIO
from typing import List

def normalize_scores(distances: List[float]) -> List[float]:
    """Normalizes a list of distances to a confidence score between 0 and 1."""
    if not distances:  # Check if the list is empty
        return []
    max_distance = max(distances)
    min_distance = min(distances)
    # Handle the case where all distances are equal
    if max_distance == min_distance:
        return [1.0 for _ in distances]
    normalized_scores = [(max_distance - d) / (max_distance - min_distance) for d in distances]
    return normalized_scores

def get_confidence_color(score: float) -> str:
    """Returns a color code based on the confidence score."""
    if score > 0.75:
        return "green"
    elif score > 0.5:
        return "orange"
    else:
        return "red"

def extract_relevant_context(data: str, question: str) -> str:
    """Extracts the most relevant rows from the data based on the question."""
    try:
        # Attempt to read the context string into a DataFrame
        from io import StringIO
        import pandas as pd

        # Read CSV and skip bad lines if necessary
        df = pd.read_csv(StringIO(data), on_bad_lines="skip")

        if "overpriced" in question.lower():
            # Calculate the average competitor rate
            competitor_columns = [col for col in df.columns if "Competitor" in col]
            df["Average Competitor Rate"] = df[competitor_columns].mean(axis=1)
            
            # Filter rows where 'Your Rate' is greater than 'Average Competitor Rate'
            overpriced_days = df[df["Your Rate"] > df["Average Competitor Rate"]]
            
            if overpriced_days.empty:
                return "No days found where your rate is overpriced compared to competitors."
            
            # Return only relevant rows
            return overpriced_days.to_csv(index=False)
        
        # Default to returning the whole dataset
        return data
    except pd.errors.ParserError as e:
        # Return detailed feedback for CSV parsing issues
        return f"Error processing the data: {str(e)}. Ensure your file has consistent columns."
    except Exception as e:
        # Catch other errors and log them
        return f"Unable to extract relevant context due to an unexpected error: {str(e)}"

def format_response(raw_response: str, context: str, question: str) -> str:
    """Formats the response to include relevant data in a user-friendly way."""
    if "overpriced" in question.lower():
        if "No days found" in context:
            return f"### Answer\n\n{context}"
        return f"### Answer\n\nYou are overpriced on the following days:\n\n{context}"
    
    return f"### Response\n\n{raw_response}"