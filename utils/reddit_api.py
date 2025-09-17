import os
import praw
import pandas as pd

def fetch_reddit_comments(output_path="data/raw/reddit_raw.csv"):
    reddit = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent=os.getenv("USER_AGENT")
    )

    subreddits = ["datascience", "python", "aws", "machinelearning"]
    comments = []

    for sub in subreddits:
        for comment in reddit.subreddit(sub).comments(limit=500):
            comments.append({
                "id": comment.id,
                "author": str(comment.author),
                "subreddit": comment.subreddit.display_name,
                "body": comment.body,
                "created_utc": comment.created_utc
            })

    df = pd.DataFrame(comments)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} comments to {output_path}")
