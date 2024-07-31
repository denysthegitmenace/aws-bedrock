terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    docker = {
      source = "kreuzwerker/docker"
    }
  }
  backend "s3" {
    bucket = "dod-iac"
    key    = "bedrock-agent/state"
    region = "eu-central-1"
  }
}

provider "aws" {
  region = "us-east-1"
}