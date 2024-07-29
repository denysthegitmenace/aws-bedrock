table_details = {
    "impect_data_cleaned": "Stats on football players and their game performance. The granularity is one row per game per player."
}

SQL_TEMPLATE_STR = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    You can order the results by a relevant column to return the most interesting examples in the database.\n\n
    Never query for all the columns from a specific table, only ask for a few relevant columns given the question.\n\n
    Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist.
    Qualify column names with the table name when needed.

    If a column name contains a space, always wrap the column name in double quotes.

    You are required to use the following format, each taking one line:\n\nQuestion: Question here\nSQLQuery: SQL Query to run\n
    SQLResult: Result of the SQLQuery\nAnswer: Final answer here\n\nOnly use tables listed below.\n{schema}\n\n
    Do not under any circumstance use SELECT * in your query.

    Here are some useful examples:
    {few_shot_examples}

    Question: {query_str}\nSQLQuery: """

RESPONSE_TEMPLATE_STR = """If the <SQL Response> below contains data, then given an input question, synthesize a response from the query results.
    If the <SQL Response> is empty, then you should not synthesize a response and instead respond that no data was found for the quesiton..\n

    \nQuery: {query_str}\nSQL: {sql_query}\n<SQL Response>: {context_str}\n</SQL Response>\n

    Do not make any mention of queries or databases in your response, instead you can say 'according to the latest information' .\n\n
    Please make sure to mention any additional details from the context supporting your response.
    If the final answer contains <dollar_sign>$</dollar_sign>, ADD '\' ahead of each <dollar_sign>$</dollar_sign>.

    Response: """
