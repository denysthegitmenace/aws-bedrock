resource "aws_bedrockagent_agent" "bedrock_agent" {
  agent_name                  = "bedrock-agent"
  agent_resource_role_arn     = aws_iam_role.agent_service_role.arn
  idle_session_ttl_in_seconds = 500
  description                 = "An agent for just about any challenge"
  instruction                 = "Do your best to answer user questions. Be friendly, kind, and wise."
  foundation_model            = "anthropic.claude-3-sonnet-20240229-v1:0"
  tags = {
    Terraform = "true"
  }
}


resource "aws_bedrockagent_agent_action_group" "query_structured_data" {
  action_group_name          = "query-structured-data"
  agent_id                   = aws_bedrockagent_agent.bedrock_agent.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  action_group_executor {
    lambda = aws_lambda_function.query_structured_data.arn
  }
  api_schema {
    s3 {
      s3_bucket_name = aws_s3_object.action_mapping.bucket
      s3_object_key  = aws_s3_object.action_mapping.key
    }
  }
}

resource "aws_s3_object" "action_mapping" {
  bucket = aws_s3_bucket.bedrock_agent.bucket
  key    = "action_mapping_schema.yaml"
  source = "../config/action_mapping_schema.yaml"
  etag   = filemd5("../config/action_mapping_schema.yaml")
}