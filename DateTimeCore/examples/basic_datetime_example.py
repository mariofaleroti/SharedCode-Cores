from date_time_core import create_timestamp_pair, utc_now_iso


print(f"UTC: {utc_now_iso()}")

utc_value, local_value = create_timestamp_pair()
print(f"UTC pair: {utc_value}")
print(f"Local pair: {local_value}")
