# Databricks notebook source
# MAGIC %md
# MAGIC # Sales Analytics Demo
# MAGIC 
# MAGIC This notebook demonstrates how to ingest a small retail dataset into Databricks and produce a few sample insights. Before ru
# MAGIC nning the cells ensure the CSV files from this repository have been uploaded to **`dbfs:/FileStore/tables/sales_demo/`** (see
# MAGIC  the project README for instructions).

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configure dataset locations
# MAGIC Update the `DATASET_ROOT` variable if you uploaded the files to a different DBFS path.

# COMMAND ----------

DATASET_ROOT = "dbfs:/FileStore/tables/sales_demo"
CUSTOMERS_PATH = f"{DATASET_ROOT}/customers.csv"
PRODUCTS_PATH = f"{DATASET_ROOT}/products.csv"
SALES_PATH = f"{DATASET_ROOT}/sales.csv"

spark.conf.set("datasets.sales_demo.root", DATASET_ROOT)

print(f"Using dataset root: {DATASET_ROOT}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Load the raw data as DataFrames

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T



def preview(df, n=20):
    if 'display' in globals():
        display(df)
    else:
        df.show(n=n, truncate=False)

schema_customers = T.StructType([
    T.StructField("customer_id", T.IntegerType(), nullable=False),
    T.StructField("first_name", T.StringType(), nullable=False),
    T.StructField("last_name", T.StringType(), nullable=False),
    T.StructField("email", T.StringType(), nullable=False),
    T.StructField("gender", T.StringType(), nullable=True),
    T.StructField("country", T.StringType(), nullable=True),
])

schema_products = T.StructType([
    T.StructField("product_id", T.IntegerType(), nullable=False),
    T.StructField("product_name", T.StringType(), nullable=False),
    T.StructField("category", T.StringType(), nullable=True),
    T.StructField("price", T.DoubleType(), nullable=False),
])

schema_sales = T.StructType([
    T.StructField("sale_id", T.IntegerType(), nullable=False),
    T.StructField("customer_id", T.IntegerType(), nullable=False),
    T.StructField("product_id", T.IntegerType(), nullable=False),
    T.StructField("quantity", T.IntegerType(), nullable=False),
    T.StructField("sale_date", T.DateType(), nullable=False),
])

customers_df = (
    spark.read
    .option("header", True)
    .schema(schema_customers)
    .csv(CUSTOMERS_PATH)
)

products_df = (
    spark.read
    .option("header", True)
    .schema(schema_products)
    .csv(PRODUCTS_PATH)
)

sales_df = (
    spark.read
    .option("header", True)
    .schema(schema_sales)
    .csv(SALES_PATH)
)

print(f"Customers: {customers_df.count()} rows")
print(f"Products: {products_df.count()} rows")
print(f"Sales: {sales_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Build a consolidated sales view

# COMMAND ----------

enriched_sales_df = (
    sales_df
    .join(customers_df, on="customer_id", how="inner")
    .join(products_df, on="product_id", how="inner")
    .withColumn("gross_revenue", F.col("quantity") * F.col("price"))
)

enriched_sales_df.createOrReplaceTempView("sales_enriched")

preview(enriched_sales_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Top products by revenue

# COMMAND ----------

top_products_df = (
    enriched_sales_df
    .groupBy("product_id", "product_name", "category")
    .agg(
        F.sum("quantity").alias("total_units"),
        F.sum("gross_revenue").alias("total_revenue"),
    )
    .orderBy(F.col("total_revenue").desc())
)

preview(top_products_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Revenue by country and gender

# COMMAND ----------

revenue_by_country_gender_df = (
    enriched_sales_df
    .groupBy("country", "gender")
    .agg(
        F.sum("gross_revenue").alias("total_revenue"),
        F.countDistinct("customer_id").alias("unique_customers"),
    )
    .orderBy(F.col("total_revenue").desc())
)

preview(revenue_by_country_gender_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Persist the curated sales view as a Delta table (optional)

# COMMAND ----------

from pyspark.sql import SparkSession

spark: SparkSession

delta_path = f"{DATASET_ROOT}/tables/sales_enriched_delta"

(enriched_sales_df
 .write
 .format("delta")
 .mode("overwrite")
 .save(delta_path)
)

spark.sql("CREATE DATABASE IF NOT EXISTS sales_demo")
spark.sql(f"DROP TABLE IF EXISTS sales_demo.sales_enriched")
spark.sql(f"CREATE TABLE sales_demo.sales_enriched USING DELTA LOCATION '{delta_path}'")

print(f"Delta table available at sales_demo.sales_enriched (path: {delta_path})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Clean up (optional)
# MAGIC Run the cell below to remove the Delta table and files created by this demo.

# COMMAND ----------

spark.sql("DROP TABLE IF EXISTS sales_demo.sales_enriched")
databricks_utils = dbutils if 'dbutils' in globals() else None

if databricks_utils is not None:
    try:
        databricks_utils.fs.rm(delta_path, recurse=True)
        print(f"Removed {delta_path}")
    except Exception as exc:  # noqa: F841 - informational message for notebook users
        print(f"Warning: unable to delete {delta_path}: {exc}")
else:
    print("dbutils not available; skipping DBFS cleanup.")
