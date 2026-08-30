from pyspark import pipelines as dp
import pyspark.sql.functions as F

# Initialize the target Silver table for SCD Type 1
dp.create_streaming_table(
    name="02_silver.dim_menu_items",
    comment="Menu Items Dimension table keeping only the latest state (SCD Type 1) via Lakeflow Connect",
    table_properties={"quality": "silver"}
)

# Read the incremental CDC logs from Bronze
@dp.view(name="v_menu_items_cdc_clean")
@dp.expect_or_drop("valid_item", "item_id IS NOT NULL AND price > 0")
def v_menu_items_cdc_clean():
    return (
        dp.read_stream("01_bronze.menu_items")
        .withColumn("price", F.col("price").cast("decimal(10,2)"))
        .withColumn("updated_at", F.to_timestamp("updated_at"))
        .select("item_id", "restaurant_id", "name", "category", "price", "is_vegetarian", "updated_at", "cdc_operation")
    )

# Apply changes (upsert) with the current Lakeflow AUTO CDC API
dp.create_auto_cdc_flow(
    target="02_silver.dim_menu_items",
    source="v_menu_items_cdc_clean",
    keys=["item_id"],
    sequence_by=F.col("updated_at"),
    
    stored_as_scd_type=1,
    apply_as_deletes=F.expr("cdc_operation = 'DELETE'")
)
