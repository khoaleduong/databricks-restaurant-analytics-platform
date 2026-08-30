from pyspark import pipelines as dp
import pyspark.sql.functions as F

# Customer SCD2 contract:
# - customer_id is the business key.
# - updated_at orders changes and must come from external CDC ingestion.
# - name, email, phone, and city are historized.
# - cdc_operation and updated_at are Bronze contract fields; this repo does
#   not configure Lakeflow Connect.
# - The source must reject conflicting records with the same key and sequence.
# - Replaying an unchanged record does not create a new version.
dp.create_streaming_table(
    name="02_silver.dim_customers",
    comment="Customer Dimension table with history tracking (SCD Type 2) synced via Lakeflow Connect",
    table_properties={"quality": "silver"}
)

# Read the CDC feed mapped into the Bronze contract.
@dp.view(name="v_customers_cdc_clean")
@dp.expect_all_or_drop({
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_email": "cdc_operation = 'DELETE' OR email LIKE '%@%'",
    "valid_updated_at": "updated_at IS NOT NULL",
    "valid_cdc_operation": "cdc_operation IN ('INSERT', 'UPDATE', 'DELETE')"
})
def v_customers_cdc_clean():
    return (
        # This is a Delta stream, not a Kafka source.
        dp.read_stream("01_bronze.customers")
        
        .withColumn("name", F.trim(F.col("name")))
        .withColumn("city", F.upper(F.trim(F.col("city"))))
        
        .withColumn("updated_at", F.to_timestamp("updated_at"))
        
        .select("customer_id", "name", "email", "phone", "city", "join_date", "updated_at", "cdc_operation")
    )

# AUTO CDC closes the current version on delete and keeps historical versions.
dp.create_auto_cdc_flow(
    target="02_silver.dim_customers",
    source="v_customers_cdc_clean",
    keys=["customer_id"],
    sequence_by=F.col("updated_at"),
    
    stored_as_scd_type=2,
    track_history_column_list=["name", "email", "phone", "city"],
    apply_as_deletes=F.expr("cdc_operation = 'DELETE'")
)
