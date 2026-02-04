import pandas as pd

def parse_csv(file_path: str):
    df = pd.read_csv(file_path)
    df = df.fillna("")
    return df.to_dict(orient="records")
