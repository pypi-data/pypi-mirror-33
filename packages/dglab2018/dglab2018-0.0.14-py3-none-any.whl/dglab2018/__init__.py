import google.datalab.bigquery as bq


def execute_raw_query(queryStr):
  query = bq.Query(queryStr))
  outputOptions = bq.QueryOutput.table(use_cache=False)
  return query.execute(output_options=outputOptions).result()

def execute_query(queryStr, dataset):
  query = bq.Query(queryStr.format(dataset))
  outputOptions = bq.QueryOutput.table(use_cache=False)
  return query.execute(output_options=outputOptions).result()

def execute_parametrized_query(client, queryStr, dataset, queryParams):
  query = queryStr.format(dataset)
  jobConfig = bq.QueryJobConfig()
  jobConfig.query_parameters = queryParams
  queryJob = client.query(
      query,
      job_config=jobConfig)  
  return queryJob.result()