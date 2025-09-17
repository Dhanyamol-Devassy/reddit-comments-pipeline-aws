import os
from datetime import datetime
import boto3
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
# Import Reddit API helper
from utils import reddit_api as api
# Load config from environment (.env)
S3_BUCKET = os.getenv("S3_BUCKET")
SILVER_JOB_NAME = os.getenv("GLUE_SILVER_JOB")
GOLD_JOB_NAME = os.getenv("GLUE_GOLD_JOB")
ATHENA_DB = os.getenv("ATHENA_DB")
ATHENA_OUTPUT = os.getenv("ATHENA_OUTPUT")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# Reddit API creds from env
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

default_args = {
    "owner": "dhanya",
    "depends_on_past": False,
    "retries": 1,
}
# Upload helper using S3Hook
def upload_to_s3(local_path, bucket, key):
    hook = S3Hook(aws_conn_id="aws_default")
    hook.load_file(
        filename=local_path,
        key=key,
        bucket_name=bucket,
        replace=True
    )
    print(f"Uploaded {local_path} to s3://{bucket}/{key}")

# Run Glue Job using boto3
def run_glue_job(job_name, script_args, region="us-east-1"):
    client = boto3.client("glue", region_name=region)
    response = client.start_job_run(
        JobName=job_name,
        Arguments=script_args
    )
    run_id = response["JobRunId"]
    print(f"Started Glue job {job_name}, RunId={run_id}")
    return run_id
with DAG(
    dag_id="reddit_end_to_end_pipeline",
    default_args=default_args,
    description="Reddit API → S3 Bronze → Glue Silver → Glue Gold → Athena validation",
    schedule_interval="@daily",
    start_date=datetime(2025, 9, 16),
    catchup=False,
) as dag:
    # Task 1: Extract Reddit data
    extract_task = PythonOperator(
        task_id="extract_reddit",
        python_callable=api.fetch_reddit_comments,
        op_kwargs={
            "output_path": "data/raw/reddit_raw.csv",
            "client_id": REDDIT_CLIENT_ID,
            "client_secret": REDDIT_CLIENT_SECRET,
            "user_agent": REDDIT_USER_AGENT,
        },    )
    # Task 2: Upload to S3 Bronze (partitioned daily)
    def upload_partitioned(**kwargs):
        today = datetime.now().strftime("%Y/%m/%d")
        key = f"reddit/bronze/{today}/reddit_raw.csv"
        upload_to_s3("data/raw/reddit_raw.csv", S3_BUCKET, key)
    upload_task = PythonOperator(
        task_id="upload_to_s3_bronze",
        python_callable=upload_partitioned,
        provide_context=True,
    )

    # Task 3: Run Glue Silver Job
    glue_silver = PythonOperator(
        task_id="glue_silver_job",
        python_callable=run_glue_job,
        op_kwargs={
            "job_name": SILVER_JOB_NAME,
            "script_args": {"--S3_BUCKET": S3_BUCKET},
            "region": AWS_REGION,
        },
    )

    # Task 4: Run Glue Gold Job
    glue_gold = PythonOperator(
        task_id="glue_gold_job",
        python_callable=run_glue_job,
        op_kwargs={
            "job_name": GOLD_JOB_NAME,
            "script_args": {"--S3_BUCKET": S3_BUCKET},
            "region": AWS_REGION,
        },
    )

    # Task 5: Repair Silver partitions in Athena
    repair_silver = AthenaOperator(
        task_id="athena_repair_silver",
        query=f"MSCK REPAIR TABLE {ATHENA_DB}.reddit_silver;",
        database=ATHENA_DB,
        output_location=ATHENA_OUTPUT,
        aws_conn_id="aws_default",
    )

    # Task 6: Repair Gold partitions in Athena
    repair_gold = AthenaOperator(
        task_id="athena_repair_gold",
        query=f"MSCK REPAIR TABLE {ATHENA_DB}.reddit_gold;",
        database=ATHENA_DB,
        output_location=ATHENA_OUTPUT,
        aws_conn_id="aws_default",
    )

    # Task 7: Validate Gold Data
    validation = AthenaOperator(
        task_id="athena_validate_gold",
        query=f"""
            SELECT subreddit,
                   SUM(comment_count) AS total_comments,
                   AVG(avg_sentiment) AS avg_sentiment
            FROM {ATHENA_DB}.reddit_gold
            GROUP BY subreddit
            ORDER BY total_comments DESC
            LIMIT 5;
        """,
        database=ATHENA_DB,
        output_location=ATHENA_OUTPUT,
        aws_conn_id="aws_default",
    )

    # DAG Flow
    extract_task >> upload_task >> glue_silver >> glue_gold >> [repair_silver, repair_gold] >> validation
