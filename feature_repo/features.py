from datetime import timedelta
from feast import Entity, FeatureView, Field, PushSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import PostgreSQLSource
from feast.types import Float32, Float64, Int64

user = Entity(name="user", join_keys=["user_id"])

credit_score_source = PostgreSQLSource(
    name="user_credit_scores",
    query="SELECT user_id, credit_score, event_timestamp FROM user_credit_scores",
    timestamp_field="event_timestamp",
)

user_credit_score_view = FeatureView(
    name="user_credit_score_fv",
    entities=[user],
    ttl=timedelta(days=30),
    schema=[Field(name="credit_score", dtype=Int64)],
    source=credit_score_source,
    online=True,
)

stats_batch_source = PostgreSQLSource(
    name="transaction_stats_source",
    query="""SELECT user_id, transaction_count_10m, total_amount_10m,
                    distance_from_home, distance_from_last_transaction,
                    ratio_to_median_purchase_price, repeat_retailer,
                    used_chip, used_pin_number, online_order,
                    event_timestamp
             FROM transaction_stats""",
    timestamp_field="event_timestamp",
)

stats_push_source = PushSource(
    name="transaction_stats_push",
    batch_source=stats_batch_source,
)

transaction_stats_view = FeatureView(
    name="transaction_stats_fv",
    entities=[user],
    ttl=timedelta(minutes=10),
    schema=[
        Field(name="transaction_count_10m", dtype=Int64),
        Field(name="total_amount_10m", dtype=Float32),
        Field(name="distance_from_home", dtype=Float64),
        Field(name="distance_from_last_transaction", dtype=Float64),
        Field(name="ratio_to_median_purchase_price", dtype=Float64),
        Field(name="repeat_retailer", dtype=Int64),
        Field(name="used_chip", dtype=Int64),
        Field(name="used_pin_number", dtype=Int64),
        Field(name="online_order", dtype=Int64),
    ],
    source=stats_push_source,
    online=True,
)