# Data dictionary

These names match the pipeline code. The SQL files are reference schemas, not a
second deployment path.

| Layer | Table | Grain / key | Upstream | Purpose |
|---|---|---|---|---|
| Bronze | `01_bronze.orders` | One typed Event Hubs message; `order_id` | Azure Event Hubs | Replayable order events |
| Bronze | `01_bronze.customers` | Source CDC record; `customer_id` | External Azure SQL CDC ingestion | Customer CDC feed |
| Bronze | `01_bronze.restaurants` | Source row; `restaurant_id` | External Azure SQL ingestion | Restaurant source used by current Gold outputs |
| Bronze | `01_bronze.menu_items` | Source row; `(restaurant_id, item_id)` | External Azure SQL ingestion | Menu source |
| Bronze | `01_bronze.reviews` | Source review; `review_id` | External Azure SQL ingestion | Review source |
| Silver | `02_silver.fact_orders` | One row per immutable logical order; `order_id` | `01_bronze.orders` | Order facts with watermark deduplication |
| Silver | `02_silver.fact_order_items` | One row per `(order_id, item_id)` | `01_bronze.orders` | Exploded item facts |
| Silver | `02_silver.dim_customers` | SCD2 versions by `customer_id` | `01_bronze.customers` | Historized customer dimension |
| Silver | `02_silver.dim_menu_items` | Latest row by `(restaurant_id, item_id)` | `01_bronze.menu_items` | Current menu dimension |
| Silver | `02_silver.fact_reviews` | One row per `review_id` | `01_bronze.reviews` | Validated/enriched reviews |
| Gold | `03_gold.d_sales_summary` | One row per `order_date` | `02_silver.fact_orders` | Realized daily sales KPIs |
| Gold | `03_gold.d_customer_360` | One current row per `customer_id` | Silver facts + current `dim_customers` | Current customer profile |
| Gold | `03_gold.d_restaurant_reviews` | One row per `restaurant_id` | `01_bronze.restaurants` + `02_silver.fact_reviews` | Restaurant review metrics |

`02_silver.dim_restaurants` is not an executable table in this repository; it
appears only in the reference schema/logical diagram.
