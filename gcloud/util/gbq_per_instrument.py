"""Run a BigQuery against each instrument in Google Big Query"""

from google.cloud import bigquery

client = bigquery.Client()
query_job = client.query("""""")

results = query_job.result()  # Waits for job to complete.
for result in results:
    print(results)
