from pyspark import pipelines as dp
import pyspark.sql.functions as F

# Initialize the target Silver table for SCD Type 2
dp.create_streaming_table(
    name="02_silver.dim_customers",
    comment="Customer Dimension table with history tracking (SCD Type 2) synced via Lakeflow Connect",
    table_properties={"quality": "silver"}
)

# Read the incremental CDC logs from the Bronze table populated by Lakeflow Connect
@dp.view(name="v_customers_cdc_clean")
@dp.expect_all_or_drop({
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_email": "email LIKE '%@%'"
})
def v_customers_cdc_clean():
    return (
        # Using read_stream to read Delta transaction logs incrementally, NOT Kafka streaming
        dp.read_stream("01_bronze.customers")
        
        .withColumn("name", F.trim(F.col("name")))
        .withColumn("city", F.upper(F.trim(F.col("city"))))
        
        .withColumn("updated_at", F.to_timestamp("updated_at"))
        
        .select("customer_id", "name", "email", "phone", "city", "join_date", "updated_at", "cdc_operation")
    )

# Apply CDC changes to the Silver table
dp.apply_changes(
    target="02_silver.dim_customers",
    source="v_customers_cdc_clean",
    keys=["customer_id"],
    sequence_by=F.col("updated_at"),
    
    stored_as_scd_type=2,
    track_history_column_list=["city", "phone"],
    apply_as_deletes=F.expr("cdc_operation = 'DELETE'")
)