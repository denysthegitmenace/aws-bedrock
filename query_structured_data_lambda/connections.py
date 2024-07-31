import os
import boto3
from llama_index.llms.bedrock import Bedrock
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Connections:
    region_name = "us-east-1"
    athena_bucket_name = os.getenv("ATHENA_BUCKET_NAME", "d98-athena-results-us-east-1")
    text2sql_database = os.getenv("TEXT2SQL_DATABASE", "d98-ai-agent")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    fewshot_examples_path = os.getenv(
        "FEWSHOT_EXAMPLES_PATH",
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "dynamic_examples.csv"
        ),
    )
    s3_resource = boto3.resource("s3", region_name=region_name)
    bedrock_client = boto3.client("bedrock-runtime", region_name=region_name)

    @staticmethod
    def get_bedrock_llm(model_name, max_tokens=256):
        MODELID_MAPPING = {
            "Claude2": "anthropic.claude-v2:1",
            "Claude3": "anthropic.claude-3-sonnet-20240229-v1:0",
            "Claude35": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        }

        MODEL_KWARGS = {
            "max_tokens": max_tokens,
            "temperature": 0,
        }
        model_kwargs = MODEL_KWARGS.copy()

        model_kwargs.update(
            {
                "model": MODELID_MAPPING[model_name],
                "region_name": Connections.region_name,
            }
        )

        llm = Bedrock(**model_kwargs)
        logger.info(f"Using follwoing FM: {model_kwargs}")

        return llm