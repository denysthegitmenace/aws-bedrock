# resource "aws_lambda_function" "query_structured_data" {
#   function_name    = "query-structured-data"
#   role             = "TODO"
#   package_type     = "Image"
#   image_uri        = docker_registry_image.query_structured_data_action_group_registry_image.image_uri
#   source_code_hash = trimprefix(docker_registry_image.query_structured_data_action_group_registry_image.id, "sha256:")
#   timeout          = 60
#   memory_size      = 3007
#   environment {
#     variables = {
#       LOG_LEVEL = "INFO"
#     }
#   }
# }