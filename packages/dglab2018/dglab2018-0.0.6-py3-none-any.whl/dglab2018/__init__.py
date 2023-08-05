import google.datalab.bigquery as bq

def execute_query(queryStr):
  query = bq.Query(queryStr.format(dataset))
  outputOptions = bq.QueryOutput.table(use_cache=False)
  return query.execute(output_options=outputOptions).result()