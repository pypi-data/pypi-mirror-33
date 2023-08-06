import google.datalab.bigquery as bq

def execute_query(queryStr, dataset):
  query = bq.Query(queryStr.format(dataset))
  outputOptions = bq.QueryOutput.table(use_cache=False)
  return query.execute(output_options=outputOptions).result()

def execute_query(queryStr, dataset, queryParams):
  query = queryStr.format(dataset)
  jobConfig = bq.QueryJobConfig()
  jobConfig.query_parameters = query_params
  queryJob = client.query(
      query,
      location='EU',
      job_config=jobConfig)  
  return queryJob.execute().result()