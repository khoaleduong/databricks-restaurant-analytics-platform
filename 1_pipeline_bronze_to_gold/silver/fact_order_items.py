from pyspark import pipelines as dp
import pyspark.sql.functions as F
from pyspark.sql.types import *

@dp.table(name="02_silver.fact_order_items")
@dp.expect_all_or_drop({
    "valid_order_id": "order_id IS NOT NULL",
    "valid_order_timestamp": "order_timestamp IS NOT NULL",
    "valid_item_id": "item_id IS NOT NULL",
    "valid_restaurant_id": "restaurant_id IS NOT NULL",
    "valid_quantity": "quantity > 0",
    "valid_unit_price": "unit_price > 0",
    "valid_subtotal": "subtotal > 0"
})
def fact_order_items():

    df = (
        dp.read_stream("01_bronze.orders")

        # standardize timestamp
        .withColumn("order_timestamp", F.to_timestamp("order_timestamp"))

        # explode items
        .withColumn("item", F.explode("items"))

        # derive date
        .withColumn("order_date", F.to_date("order_timestamp"))

        # select + flatten
        .select(
            "order_id",
            "restaurant_id",
            "order_timestamp",
            "order_date",
            F.col("item.item_id").alias("item_id"),
            F.col("item.name").alias("item_name"),
            F.col("item.category").alias("category"),
            F.col("item.quantity").alias("quantity"),
            F.col("item.unit_price").cast("decimal(10,2)").alias("unit_price"),
            F.col("item.subtotal").cast("decimal(10,2)").alias("subtotal")
        )
    )
    
    return df
