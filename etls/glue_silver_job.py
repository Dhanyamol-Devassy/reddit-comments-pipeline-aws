from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, from_unixtime, year, month, dayofmonth

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read Bronze (CSV)
df = spark.read.option("header", True).csv("s3://reddit-data-bucket-dhanya/bronze/")

# Clean + add partition columns
df_clean = (
    df.filter(col("body").isNotNull())
      .withColumn("created_ts", from_unixtime(col("created_utc")))
      .withColumn("year", year(from_unixtime("created_utc")))
      .withColumn("month", month(from_unixtime("created_utc")))
      .withColumn("day", dayofmonth(from_unixtime("created_utc")))
)

# Write to Silver as partitioned Parquet
df_clean.write.mode("overwrite").partitionBy("year","month","day") \
    .parquet("s3://reddit-data-bucket-dhanya/silver/")
