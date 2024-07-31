resource "aws_iam_role" "agent_service_role" {
  name        = "bedrock_agent_service_role"
  description = "Bedrock agent service role"
  path        = "/service-role/"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AmazonBedrockAgentBedrockFoundationModelPolicyProd",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "bedrock.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {
          "StringEquals" : {
            "aws:SourceAccount" : "${var.aws_account_id}"
          },
          "ArnLike" : {
            "aws:SourceArn" : "arn:aws:bedrock:us-east-1:${var.aws_account_id}:agent/*"
          }
        }
      }
    ]
  })

  managed_policy_arns = [
    aws_iam_policy.invoke_bedrock_fm_for_agent.arn,
  ]

  tags = {
    Terraform = "true"
  }
}


resource "aws_iam_policy" "invoke_bedrock_fm_for_agent" {
  name = "invoke_bedrock_fm_for_agent"
  path = "/service-role/"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "BedrockInvokeModelStatement",
        "Effect" : "Allow",
        "Action" : [
          "bedrock:InvokeModel"
        ],
        "Resource" : [
          "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        ]
      }
  ] })
}

resource "aws_iam_role" "query_structured_data_lambda" {
  name        = "query_structured_data_lambda_role"
  description = "For the lambda function to query structured data from Athena tables."
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}