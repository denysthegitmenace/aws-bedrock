import json
import logging

import build_query_engine
from connections import Connections

logging.basicConfig(level=Connections.log_level)
logger = logging.getLogger(__name__)

MODEL_ALIAS = "Claude3"


def log(message):
    logger.info(message)


def get_response(event, context):
    """
    Get response RAG or Query
    """

    log("Logging event:")
    log(json.dumps(event))

    query_engine = build_query_engine.create_query_engine(MODEL_ALIAS)

    responses = []

    response_code = 200
    api_path = event["apiPath"]
    parameters = event["parameters"]
    user_input = parameters[0]["value"]

    # Only allow one str, to mitigate mixed prompt injection
    if isinstance(user_input, str):
        log(f"Question {user_input}")
        if api_path in ["/querydb"]:
            response = query_engine.query(user_input)

            final_query = response.metadata["sql_query"].replace("\n", " ")
            log(f"Sql query: {final_query}")
            log(f"Provided response: {response.response}")
            output = {
                "source": response.metadata["sql_query"],
                "answer": response.response,
            }

        else:
            output = {
                "source": "Not Found",
                "answer": "I don't know enough to answer this question, please try to clarify you quesiton.",
            }

    else:
        output = {
            "source": "Not Found",
            "answer": "Please ask questions one by one.",
        }

    body = f"""
            Source: <final_sql_query>{output["source"]}</final_sql_query>
            Returned information: {output["answer"]}

            """
    response_body = {"application/json": {"body": body}}  # output["answer"]#str(body)

    action_response = {
        "actionGroup": event["actionGroup"],
        "apiPath": event["apiPath"],
        "httpMethod": event["httpMethod"],
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    responses.append(action_response)

    return {"messageVersion": "1.0", "response": action_response}
