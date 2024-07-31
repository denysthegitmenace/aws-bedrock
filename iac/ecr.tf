data "aws_ecr_authorization_token" "token" {}
provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}


### streamlit start ###
resource "aws_ecr_repository" "streamlit_app_repository" {
  name                 = "streamlit-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "docker_image" "streamlit_app_docker_image" {
  name = aws_ecr_repository.streamlit_app_repository.repository_url
  build {
    context  = "${path.cwd}/../streamlit_app"
    platform = "linux/amd64"
  }

  triggers = {
    dir_sha = sha1(join("", [for f in fileset("${path.cwd}/../streamlit_app", "**") : filesha1("${path.cwd}/../streamlit_app/${f}")]))
  }
  force_remove = true
}

resource "docker_registry_image" "streamlit_app_registry_image" {
  name          = docker_image.streamlit_app_docker_image.name
  keep_remotely = true
  triggers = {
    dir_sha = sha1(join("", [for f in fileset("${path.cwd}/../streamlit_app", "**") : filesha1("${path.cwd}/../streamlit_app/${f}")]))
  }
}
### streamlit end ###

### txt2sql lambda start ###
resource "aws_ecr_repository" "query_structured_data_lambda_repository" {
  name                 = "query-structured-data-lambda"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

data "aws_ecr_image" "query_structured_data_lambda_image" {
  repository_name = aws_ecr_repository.query_structured_data_lambda_repository.name
  image_tag       = "latest"
}

resource "docker_registry_image" "query_structured_data_lambda_registry_image" {
  name          = docker_image.query_structured_data_lambda_docker_image.name
  keep_remotely = true
  triggers = {
    dir_sha = sha1(join("", [for f in fileset("${path.cwd}/../query_structured_data_lambda", "**") : filesha1("${path.cwd}/../query_structured_data_lambda/${f}")]))
  }
}

resource "docker_image" "query_structured_data_lambda_docker_image" {
  name = aws_ecr_repository.query_structured_data_lambda_repository.repository_url
  build {
    context  = "${path.cwd}/../query_structured_data_lambda"
    platform = "linux/amd64"
  }

  triggers = {
    dir_sha = sha1(join("", [for f in fileset("${path.cwd}/../query_structured_data_lambda", "**") : filesha1("${path.cwd}/../query_structured_data_lambda/${f}")]))
  }
  force_remove = true
}
### txt2sql lambda end ###