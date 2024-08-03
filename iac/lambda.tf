resource "aws_lambda_function" "query_structured_data" {
  function_name    = "query-structured-data"
  role             = aws_iam_role.query_structured_data_lambda.arn
  package_type     = "Image"
  image_uri        = data.aws_ecr_image.query_structured_data_lambda_image.image_uri
  source_code_hash = trimprefix(docker_registry_image.query_structured_data_lambda_registry_image.id, "sha256:")
  timeout          = 60
  memory_size      = 3007
  environment {
    variables = {
      LOG_LEVEL = "INFO"
      ATHENA_BUCKET_NAME = "aws-athena-query-results-us-east-1-435301922904"
      TARGET_DB = "main"
    }
  }
}
