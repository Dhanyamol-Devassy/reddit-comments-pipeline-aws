# Reddit Data Engineering Project

## 📌 Introduction
This project demonstrates an **end-to-end data engineering pipeline** for extracting Reddit comments via the Reddit API, processing them with **Apache Airflow** and **AWS Glue**, storing data in **Amazon S3** (Bronze → Silver → Gold layers), querying curated datasets with **Amazon Athena**, and finally creating interactive dashboards in **Amazon QuickSight**.

The workflow follows a modern **medallion architecture**:
- **Bronze Layer**: Raw Reddit data (JSON/CSV) ingested directly from Reddit API.
- **Silver Layer**: Cleaned & structured data stored in partitioned Parquet format.
- **Gold Layer**: Aggregated data with sentiment scores for analytics & visualization.

---

## 🚀 Tech Stack
- **Apache Airflow** (Dockerized) → Workflow orchestration  
- **Reddit API** → Data ingestion  
- **Amazon S3** → Data Lake (Bronze, Silver, Gold layers)  
- **AWS Glue Jobs** → ETL & Sentiment Analysis  
- **AWS Glue Catalog** → Schema management  
- **Amazon Athena** → Querying processed data  
- **Amazon QuickSight** → Visualization  

---

## 📂 Project Structure
```
REDDITDATAENGINEERING/
│── config/
│   └── airflow.env                   # Environment variables (Reddit API & AWS credentials)
│── dag/
│   └── reddit_pipeline.py            # Airflow DAG for orchestration
│── data/                             # Sample input/output data
│── etls/
│   ├── glue_silver_job.py            # Glue job: Clean & transform raw data
│   └── glue_gold_job.py              # Glue job: Sentiment analysis + aggregation
│── utils/
│   ├── reddit_api.py                 # Utility for Reddit API extraction
│   └── reddit_etl.py                 # Helper functions for ETL
│── docker-compose.yml                # Airflow setup
│── requirements.txt                  # Python dependencies
│── .gitignore                        # Ignore venv, __pycache__, logs, creds
│── docs/
│   └── Detailed_Project_Report.docx  # Full documentation
│── README.md
```

---

## 🔑 Setup Instructions

### 1️⃣ Reddit API Credentials
- Create a Reddit app at [Reddit Apps](https://www.reddit.com/prefs/apps).
- Get your `client_id`, `client_secret`, and `user_agent`.

### 2️⃣ Configure Airflow Environment
Add the credentials in `config/airflow.env`:
```
REDDIT_CLIENT_ID=xxxx
REDDIT_CLIENT_SECRET=xxxx
REDDIT_USER_AGENT=xxxx
AWS_ACCESS_KEY_ID=xxxx
AWS_SECRET_ACCESS_KEY=xxxx
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=reddit-data-bucket-dhanya
GLUE_SILVER_JOB=silver_job
GLUE_GOLD_JOB=gold_job
GLUE_ROLE=reddit-role
ATHENA_DB=redditdb
ATHENA_OUTPUT=s3://reddit-data-bucket-dhanya/athena-results/
```

### 3️⃣ Start Airflow (Docker)
```bash
docker compose up -d
```
Airflow UI → [http://localhost:8080](http://localhost:8080)

### 4️⃣ Trigger the DAG
Run the DAG: **reddit_pipeline**  
Steps executed:
1. Extract Reddit data  
2. Upload raw data → S3 Bronze  
3. Run Glue Silver job → Cleaning & partitioning  
4. Run Glue Gold job → Sentiment + aggregation  
5. Repair Athena tables (Silver, Gold)  
6. Validate aggregated data in Athena  

---

## 📊 QuickSight Dashboards
Dashboards created using **reddit_gold dataset**:
- **Top Subreddits by Comment Count** → Horizontal Bar Chart  
- **Average Sentiment by Subreddit** → Colored Bar Chart (Red = Negative, Green = Positive)  
- **Comments Trend Over Time** → Line Chart (subreddit-wise)  
- **Sentiment Distribution** → Pie Chart (Positive, Neutral, Negative)  
- **Subreddit Heatmap** → (Day × Subreddit by activity)  
- **Sentiment vs Comments** → Scatter Plot  

---

## 📘 Documentation
Full detailed report with **intro, ETL steps, Glue jobs, QuickSight visuals, troubleshooting, and cost optimization** is available in the `docs/` folder.

---

## ✨ Future Enhancements
- Add real-time ingestion with **Kinesis Data Streams**.  
- Extend sentiment analysis with **HuggingFace NLP models**.  
- Deploy to production with **CI/CD (GitHub Actions + Terraform IaC)**.  

---

## 👨‍💻 Author
**Dhanyamol Devassy**   
SDET & AWS Data Engineering Enthusiast  
