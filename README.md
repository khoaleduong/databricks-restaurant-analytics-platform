# Databricks Restaurant Analytics Platform

A Databricks restaurant analytics project built with synthetic source data. It
shows an Azure Event Hubs and Azure SQL flow, Spark Declarative Pipelines,
Bronze/Silver/Gold tables, streaming deduplication, AUTO CDC SCD Type 2, and
focused validation.

The platform produces three analytical outputs:

- realized sales KPIs;
- a current-state customer 360 profile;
- restaurant review and sentiment summaries.

This is a portfolio implementation, not a fully provisioned production
platform.

## Architecture at a glance

```text
Synthetic generators / source systems
        |-- Azure SQL master data + SQL Server CDC (external setup)
        |-- Azure Event Hubs immutable order events (external resource)
        v
01_bronze
        |-- raw/typed orders from Event Hubs
        |-- source tables/CDC feeds from external ingestion
        v
02_silver
        |-- fact_orders (event-time deduplication)
        |-- fact_order_items (same order-level rule, then explode)
        |-- dim_customers (native AUTO CDC SCD Type 2)
        |-- dim_menu_items (native AUTO CDC SCD Type 1)
        |-- fact_reviews (quality rules + AI enrichment)
        v
03_gold
        |-- d_sales_summary
        |-- d_customer_360
        |-- d_restaurant_reviews
```

The pipeline definitions are under
[`1_pipeline_bronze_to_gold/`](1_pipeline_bronze_to_gold/). The PNG diagrams
are visual references. The current implementation diagram is
[`diagrams/current_architecture.md`](diagrams/current_architecture.md). This
flow and the table inventory below describe what is implemented today. The
older star-schema image includes the planned restaurant Silver dimension; it is
a logical model, not a deployment claim.

## Implementation status

| Component | Status | Repository boundary |
|---|---|---|
| Synthetic customers, restaurants, menu items, orders, reviews | Implemented | `0_synthetic_data/` |
| Azure Event Hubs producer | Implemented code; external resource required | `04_eventhub_orders.py` |
| Azure SQL source DDL and CDC setup examples | Reference/setup guidance | `sql/azuresqldatabase_setup.sql` |
| Lakeflow Connect ingestion | External/manual configuration | Not provisioned here |
| Lakeflow Declarative Pipeline transformations | Implemented | `1_pipeline_bronze_to_gold/` |
| Bronze/Silver/Gold tables | Implemented through pipeline definitions | Runtime catalog/schema required |
| AUTO CDC SCD Type 2 customer dimension | Implemented in pipeline code | Requires external Bronze CDC contract |
| Unity Catalog | External deployment capability | No catalog provisioning in repository |
| Databricks Workflows | External deployment capability | No job definition in repository |
| Mosaic AI `ai_query` review enrichment | Implemented SQL transformation; model/workspace access external | `silver/fact_reviews.sql` |
| AI/BI dashboards | External/manual consumption layer | Dashboard definitions are not included |
| `02_silver.dim_restaurants` | Reference/planned only | No executable Silver pipeline creates it |
| Custom observability, CI/CD, and IaC | Intentionally not included | Portfolio scope boundary |

## End-to-end data flow

### Sources and Bronze

The synthetic producer emits one immutable order snapshot per Event Hubs
message. `order_id` is the stable logical event identity; no separate
`event_id` is needed for this event model. Bronze parses the nested item array
into a typed source-shaped event and remains suitable for replay/debugging.

Azure SQL customers, restaurants, menu items, historical orders, and reviews
are source datasets. The repository contains setup examples, but the actual
Lakeflow Connect ingestion and its Azure resources must be configured outside
the repository.

### Silver facts and dimensions

- `fact_orders` standardizes event time and derives calendar attributes. Its
  grain is one row per immutable logical order (`order_id`).
- `fact_order_items` explodes the same canonical order event after applying the
  same replay rule. Its grain is one row per (`order_id`, `item_id`).
- `dim_customers` uses native Lakeflow AUTO CDC SCD Type 2 processing.
- `dim_menu_items` uses native Lakeflow AUTO CDC SCD Type 1 processing.
- `fact_reviews` validates rating/sentiment fields and enriches review text with
  `ai_query`; model availability is a workspace dependency.

### Gold outputs

- `d_sales_summary`: daily realized-sales metrics.
- `d_customer_360`: current customer profile, loyalty tier, spend, preferences,
  and VIP flag.
- `d_restaurant_reviews`: rating distributions and sentiment counts by
  restaurant. It currently reads the Bronze restaurant source because an
  executable conformed Silver restaurant dimension is not implemented.

## Streaming semantics

Silver applies:

```python
.withWatermark("order_timestamp", "1 day")
.dropDuplicatesWithinWatermark(["order_id"])
```

to both order fact paths before item explosion. This is event-time
deduplication, not global exactly-once processing.

- duplicates within the supported event-time watermark range are deduplicated;
- events older than the watermark may be treated as too late and dropped;
- duplicate representations whose event-time difference exceeds the configured
  threshold are not guaranteed to be deduplicated;
- the one-day duration is a portfolio/demo lateness assumption, not a measured
  production SLA.

The pipeline targets normal micro-batch Lakeflow/Structured Streaming mode on
Databricks Runtime 13.3 LTS or later. Lakeflow real-time mode does not support
`dropDuplicatesWithinWatermark`.

## CDC and SCD Type 2 semantics

The customer flow is:

```text
Azure SQL / SQL Server CDC
        v
External ingestion configuration
        v
Canonical Bronze customer CDC contract
        v
Lakeflow AUTO CDC
        v
02_silver.dim_customers
```

The canonical Bronze contract expected by this repository is:

```text
customer_id, name, email, phone, city, join_date,
updated_at, cdc_operation
```

`updated_at` is the logical sequence used by AUTO CDC. `cdc_operation` must be
`INSERT`, `UPDATE`, or `DELETE`. The physical source/connector metadata names
may differ; external ingestion must map them to this contract. The SQL source
DDL does not itself define these two fields.

`customer_id` is the business key. Changes to name, email, phone, or city create
new SCD2 versions. Deletes close the current version while preserving history.
Databricks-managed `__START_AT` and `__END_AT` columns represent version
validity. Customer 360 selects the current version with:

```python
filter(F.col("__END_AT").isNull())
```

Conflicting changes with the same customer and sequence are considered
ambiguous and must be rejected by upstream ingestion because this repository
does not contain a trustworthy tie-breaker.

## Business semantics

Only `delivered` and `completed` orders contribute to realized revenue, Gold
order counts, customer lifetime spend, and customer preferences. Operational
statuses (`pending`, `confirmed`, `preparing`, and `ready`) remain available in
Silver but do not contribute to realized sales metrics.

Favorite restaurant/item selection is deterministic: highest business metric,
then most recent relevant order, then stable restaurant/item ID.

## Validation

### Local validation

Run the focused standard-library test suite:

```bash
uv run --no-cache python -m unittest discover -s tests -v
```

The tests cover the generated payload, item shape, monetary reconciliation,
item-ID uniqueness, source references, UTC timestamps, and realized statuses.

### Pipeline expectations

The executable pipeline includes high-value expectations for order IDs and
timestamps, valid statuses/payments/amounts, positive item quantities/prices,
and review sentiment/rating ranges.

### Databricks smoke/reconciliation checks

These require a configured workspace and are not claimed as locally executed:

- replay an order within the one-day watermark and confirm both fact paths keep
  one logical order and one item set;
- run the AUTO CDC insert/change/replay/delete fixture and inspect current and
  historical rows;
- reconcile `fact_orders.total_amount` to `SUM(fact_order_items.subtotal)`;
- use anti-joins to check orders against `02_silver.dim_customers` and
  `01_bronze.restaurants` (the latter is the current restaurant source);
- exercise favorite-ranking ties and confirm count, recency, and stable-ID
  ordering.

## How to run

### Local synthetic data and validation

Install the generator dependencies from
[`0_synthetic_data/requirements.txt`](0_synthetic_data/requirements.txt), then:

```bash
uv run --no-cache python 0_synthetic_data/03_run.py
uv run --no-cache python -m unittest discover -s tests -v
```

The generator writes CSV files under `0_synthetic_data/data/` (ignored by Git).
The Event Hubs producer additionally requires the environment variables shown
in [`.env.example`](.env.example).

### External Databricks/Azure setup

End-to-end execution additionally requires:

- Azure SQL with the source tables and SQL Server CDC configuration;
- an Azure Event Hubs namespace/event hub;
- Lakeflow Connect or equivalent external ingestion mapped to the canonical
  Bronze CDC contract;
- a Databricks Runtime 13.3 LTS-or-later normal micro-batch pipeline;
- workspace/model access for the review `ai_query` transformation if enabled;
- pipeline catalog/schema and secret configuration.

This repository does not provision those resources, Databricks Workflows,
Unity Catalog objects, dashboards, or secret scopes.

## Configuration and secrets

Copy `.env.example` to `.env` for local Event Hubs execution and fill in values
locally. Do not commit `.env` or credentials. In Databricks, use the workspace's
secret-scope/key-vault mechanism and pipeline configuration for connection
values.

## Important engineering decisions

1. `order_id` is sufficient as the event identity because the producer emits one
   immutable order message rather than an order-status event stream.
2. Bronze stays replayable and typed; deduplication belongs in Silver so
   raw events remain available for debugging.
3. Event-time watermarking bounds state and makes the lateness assumption
   explicit; the project does not claim global exactly-once delivery.
4. Native AUTO CDC is used for SCD2 instead of custom MERGE logic. It handles
   sequencing, history, and deletes in the pipeline.
5. Customer 360 uses the current SCD2 row because it is a current profile, not an
   as-of historical analysis.
6. No surrogate keys were added; the source business keys are sufficient for
   this portfolio model.
7. Databricks-native streaming and AUTO CDC behavior are smoke-tested rather
   than mocked locally.
8. A Silver restaurant dimension was not added solely for symmetry; Gold uses
   the existing Bronze restaurant source and documents that limitation.

## Known limitations

These are deliberate portfolio scope boundaries:

- Azure resources and Lakeflow Connect configuration are external;
- external ingestion must map connector CDC metadata into the canonical Bronze
  contract;
- same-sequence conflicting customer changes are rejected by contract rather
  than resolved in repository code;
- the order model supports immutable order events, not legitimate status updates
  for an existing `order_id`;
- the one-day watermark is assumed rather than measured;
- there is no global exactly-once or source-level delivery claim;
- no executable `02_silver.dim_restaurants` exists;
- Databricks integration/smoke checks require a workspace;
- custom observability, CI/CD, and IaC are intentionally out of scope.

## Repository guide

```text
0_synthetic_data/              generators, source DDL, reference schemas
1_pipeline_bronze_to_gold/    Bronze ingestion, Silver transformations, Gold views
tests/                         focused local business/invariant tests
diagrams/                      visual architecture and model references
```
