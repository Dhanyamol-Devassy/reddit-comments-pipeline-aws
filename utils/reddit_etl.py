import pandas as pd, boto3, os

def extract():
    df = pd.read_csv("data/raw/reddit_raw.csv")
    df.to_csv("data/stage.csv", index=False)
    print("Extract step done")

def transform():
    df = pd.read_csv("data/stage.csv")
    df["body"] = df["body"].str.replace(r'\n', ' ', regex=True)
    df["body"] = df["body"].fillna("UNKNOWN")
    df.to_csv("data/clean.csv", index=False)
    print("Transform step done")

def load():
    s3 = boto3.client("s3")
    bucket = "reddit-data-bucket-dhanya"   # change to the desiredbucket
    s3.upload_file("data/clean.csv", bucket, "bronze/reddit_clean.csv")
    print("Uploaded to S3 Bronze")

