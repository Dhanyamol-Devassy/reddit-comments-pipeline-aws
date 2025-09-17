from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, count, avg, udf
from pyspark.sql.types import DoubleType
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
# Small lexicon
positive_words = {"good", "great", "excellent", "happy", "love", "like", "awesome"}
negative_words = {"bad", "terrible", "sad", "hate", "angry", "worst", "awful"}
def sentiment_score(text):
    if not text:
        return 0.0
    words = text.lower().split()
    score = 0
    for w in words:
        if w in positive_words:
            score += 1
        elif w in negative_words:
            score -= 1
    return float(score)
sentiment_udf = udf(sentiment_score, DoubleType())
# Read Silver
df = spark.read.parquet("s3://reddit-data-bucket-dhanya/silver/")
# Add sentiment
df_sent = df.withColumn("sentiment", sentiment_udf(col("body")))
# Aggregate into Gold
df_gold = (
    df_sent.groupBy("subreddit","year","month","day")
           .agg(
               count("id").alias("comment_count"),
               avg("sentiment").alias("avg_sentiment")
           )
)
df_gold.write.mode("overwrite").partitionBy("year","month","day") \
    .parquet("s3://reddit-data-bucket-dhanya/gold/")
