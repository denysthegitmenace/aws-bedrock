resource "aws_cloudwatch_log_group" "query_structured_data" {
  name = "/aws/lambda/query-structured-data"
}

resource "aws_cloudwatch_log_group" "fm_invocations" {
  name = "/aws/bedrock/fm-invocations"
}