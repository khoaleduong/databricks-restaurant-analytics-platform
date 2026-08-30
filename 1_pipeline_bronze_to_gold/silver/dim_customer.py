from pyspark import pipelines as dp
import pyspark.sql.functions as F

# SCD Type 2 contract
# - Business key: customer_id (from the Azure SQL source table)
# - Sequence: updated_at, supplied by the externally configured CDC ingestion
# - History attributes: descriptive customer fields that may change over time
# - cdc_operation and updated_at are connector/ingestion contract fields; this
#   repository does not provision Lakeflow Connect or define their source shape.
# - The CDC source must reject ambiguous records with the same customer_id and
#   updated_at because no trustworthy tie-breaker is present in this repository.
# - Exact replays are safe: AUTO CDC only creates a new SCD2 version when
#   a tracked attribute changes.
dp.create_streaming_table(
    name="02_silver.dim_customers",
    comment="Customer Dimension table with history tracking (SCD Type 2) synced via Lakeflow Connect",
    table_properties={"quality": "silver"}
)

# Read the incremental CDC logs from the Bronze table populated by Lakeflow Connect
@dp.view(name="v_customers_cdc_clean")
@dp.expect_all_or_drop({
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_email": "cdc_operation = 'DELETE' OR email LIKE '%@%'",
    "valid_updated_at": "updated_at IS NOT NULL",
    "valid_cdc_operation": "cdc_operation IN ('INSERT', 'UPDATE', 'DELETE')"
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

# Apply CDC changes to the Silver table with the current Lakeflow AUTO CDC API.
# Deletes close the current version; historical versions remain queryable through
# the native SCD2 history columns.
dp.create_auto_cdc_flow(
    target="02_silver.dim_customers",
    source="v_customers_cdc_clean",
    keys=["customer_id"],
    sequence_by=F.col("updated_at"),
    
    stored_as_scd_type=2,
    track_history_column_list=["name", "email", "phone", "city"],
    apply_as_deletes=F.expr("cdc_operation = 'DELETE'")
)
