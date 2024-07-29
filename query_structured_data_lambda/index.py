import build_query_engine
import json
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()


def log(message):
    logger.info(message)


def get_response(event, context):
    """
    Get response RAG or Query
    """

    log("Logging event:")
    log(json.dumps(event))

    query_engine = build_query_engine.create_query_engine(model_name="Claude35")

    responses = []

    response_code = 200
    api_path = event["apiPath"]
    parameters = event["parameters"]
    user_input = parameters[0]["value"]

    # Only allow one str, to mitigate mixed prompt injection
    if isinstance(user_input, str):

        log(f"Question {user_input}")
        if api_path in ["/playerstats"]:
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
            Source: {output["source"]}
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


if __name__ == "__main__":
    get_response(
        event={
            "agent": {
                "alias": "agent-alias",
                "name": "agent-name",
                "version": "agent-version",
                "id": "agent-id",
            },
            "sessionId": "216876597295710",
            "sessionAttributes": {},
            "promptSessionAttributes": {},
            "inputText": "How many goals did Thomas score in season 23/24?",
            "apiPath": "/playerstats",
            "httpMethod": "GET",
            "messageVersion": "1.0",
            "actionGroup": "ChatBotBedrockAgentActionGroup",
            "parameters": [
                {
                    "name": "uc2Question",
                    "type": "string",
                    "value": "How many goals did Thomas score in season 23/24?",
                }
            ],
        },
        context=None,
    )
