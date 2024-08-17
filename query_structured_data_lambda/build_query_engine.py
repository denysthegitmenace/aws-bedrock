import csv
import json
import logging

from connections import Connections
from llama_index.core import ServiceContext, SQLDatabase, VectorStoreIndex
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.core.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from llama_index.core.prompts import Prompt, PromptTemplate
from llama_index.core.schema import TextNode
from llama_index.embeddings.bedrock import BedrockEmbedding

from prompt_templates import RESPONSE_TEMPLATE_STR, SQL_TEMPLATE_STR, TABLE_DETAILS

from sqlalchemy import create_engine

# Set up logging
logging.basicConfig(level=Connections.log_level)
logger = logging.getLogger(__name__)

NUM_FEW_SHOT_EXAMPLES_TO_CONSIDER = 3
NUM_TABLES_TO_CONSIDER = 5


def create_sql_engine():
    conn_url = f"awsathena+rest://athena.{Connections.region_name}.amazonaws.com/{Connections.text2sql_database}?s3_staging_dir=s3://{Connections.athena_bucket_name}"
    return create_engine(conn_url)


def get_few_shot_retriever(embed_model):
    with open(
        Connections.fewshot_examples_path, newline="", encoding="utf-8-sig"
    ) as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True)
        data_dict = {row["example_input_question"]: row for row in reader}
        few_shot_nodes = [TextNode(text=json.dumps(q)) for q in data_dict.keys()]

    few_shot_index = VectorStoreIndex(
        few_shot_nodes,
        service_context=ServiceContext.from_defaults(embed_model=embed_model, llm=None),
    )
    return (
        few_shot_index.as_retriever(similarity_top_k=NUM_FEW_SHOT_EXAMPLES_TO_CONSIDER),
        data_dict,
    )


def few_shot_examples_fn(few_shot_retriever, data_dict, query_str, **kwargs):
    retrieved_nodes = few_shot_retriever.retrieve(query_str)
    result_strs = []
    for node in retrieved_nodes:
        content = json.loads(node.get_content())
        raw_dict = data_dict[content]
        example = [f"{k.capitalize()}: {v}" for k, v in raw_dict.items()]
        result_strs.append("\n".join(example))

    example_set = "\n\n".join(result_strs)
    logger.info(f"Example set provided:\n{example_set}")
    return example_set


def create_query_engine(model_name):
    embed_model = BedrockEmbedding(
        client=Connections.bedrock_client, model_name="amazon.titan-embed-text-v1"
    )
    few_shot_retriever, data_dict = get_few_shot_retriever(embed_model)

    sql_prompt = PromptTemplate(
        SQL_TEMPLATE_STR,
        function_mappings={
            "few_shot_examples": lambda **kwargs: few_shot_examples_fn(
                few_shot_retriever, data_dict, **kwargs
            )
        },
    )

    engine = create_sql_engine()
    sql_database = SQLDatabase(engine)

    llm = Connections.get_bedrock_llm(model_name=model_name, max_tokens=1024)
    service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
    # list of table schemas
    table_schema_objs = [
        SQLTableSchema(table_name=table, context_str=TABLE_DETAILS[table])
        for table in sql_database._all_tables
    ]

    # this is just a mechanism—not a data structure by itself
    # takes in a SQLDatabase and produces a Node object for each SQLTableSchema object passed into the ObjectIndex constructor below
    table_node_mapping = SQLTableNodeMapping(sql_database)

    # gives us a VectorStoreIndex where each Node contains table schema
    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,  # type: ignore
        service_context=service_context,
    )

    query_engine = SQLTableRetrieverQueryEngine(
        sql_database,
        obj_index.as_retriever(similarity_top_k=NUM_TABLES_TO_CONSIDER),
        service_context=service_context,
        text_to_sql_prompt=sql_prompt,
        response_synthesis_prompt=Prompt(RESPONSE_TEMPLATE_STR),
    )

    logger.info(f"prompts_dict: {query_engine.get_prompts()}")
    return query_engine
