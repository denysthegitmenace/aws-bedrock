TABLE_DETAILS = {
    "customers": "Customers purchase products from employees",
    "employees": "Employees sell products to customers",
    "orders": "Events of customers purchasing from employees",
    "products": "Products are supplied by vendors. Products belong to subcategories",
    "vendors": "Vendors supply products",
    "vendorproduct": "Use this table exclusively when joining with the 'vendors' table. Avoid using it in any other scenarios.",
    "productcategories": "Product categories are made up of multiple product subcategories",
    "productsubcategories": "Each product belongs to a product subcategory",
}

SQL_TEMPLATE_STR = """
Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for a few relevant columns given the question.
Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist.
Qualify column names with the table name when needed.

If a column name contains a space, always wrap the column name in double quotes.

You are required to use the following format, each taking one line:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use tables listed below.
{schema}

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
