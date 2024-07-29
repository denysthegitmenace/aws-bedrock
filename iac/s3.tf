resource "aws_s3_bucket" "bedrock_agent" {
  bucket = "bedrock-agent"

  tags = {
    Name = "bedrock-agent"
  }
}