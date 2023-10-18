import pymysql
import openai
import re

OPENAI_API_KEY = 'YOUR_API_KET'

HOST = 'HOST_NAME'
USER = 'USER_NAME'
PASSWORD = 'YOUR_PASSWORD'
DB_NAME = 'YOUR_DB_NAME'

db_config = {
    'host': HOST,
    'user': USER,
    'password': PASSWORD,
    'db': DB_NAME,
}

openai.api_key = OPENAI_API_KEY

# Retrieve only SQL queries from a ChatGPT response
def retrieveQuery(text):
    sql_pattern = r"SELECT[\s\S]*?;"
    sql_queries = re.findall(sql_pattern, text)
    return sql_queries

# Send a SQL query to database
# And retrieve the result
def retrieveDatabase(q):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        query = q
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()

# Send the result to ChatGPT API
# to get a formatted answer
def chatGptForAnswer(result, query, question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You will be acting as a SQL expert and giving users stock information by creating SQL queries to pull reporting from our database. 
                    We have 2 tables to work with. The first table is called 'company' that stores the profiles of the companies. 
                    It has the following columns: company_id||company_ticker||company_name||sector||industry. 
                    The second table is called 'summary' that stores the summaries of stock information of the companies. 
                    It has the following columns: date||company_id||company_ticker||price||market_cap||beta||pe_ratio||eps. 
                    And we have a view created by the following SQL query: 
                    'CREATE VIEW latest_summary AS SELECT s.* FROM summary s WHERE s.date = (SELECT MAX(date) FROM summary);' 
                    And user will give you a SQL query that they used and result. Then, you report only information relating to stock from what you are given. 
                    And show the result as a table
                    """
                },
                {
                    "role": "assistant",
                    "content": f"The question was {question}"
                },
                {
                    "role": "user",
                    "content": f"The result is {result} and the query was {query}"
                }
            ]
        )
        content = response["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        return f"Error: {str(e)}"

# Request ChatGPT to convert a user's question to a SQL query
def chatGpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You will be acting as a SQL expert and giving users stock information by creating SQL queries to pull reporting from our database. 
                    We have 2 tables to work with. The first table is called 'company' that stores the profiles of the companies. 
                    It has the following columns: company_id||company_ticker||company_name||sector||industry. 
                    The second table is called 'summary' that stores the summaries of stock information of the companies. 
                    It has the following columns: date||company_id||company_ticker||price||market_cap||beta||pe_ratio||eps. 
                    And we have a view created by the following SQL query: 
                    'CREATE VIEW latest_summary AS SELECT s.* FROM summary s WHERE s.date = (SELECT MAX(date) FROM summary);' 
                    And please show only SQL query. And when you retrieve company_name, you may need to use 'LIKE' function."""
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        content = response["choices"][0]["message"]["content"]
        queries = retrieveQuery(content)
        answers = []
        for q in queries:
            result = retrieveDatabase(q)
            answers.append(chatGptForAnswer(result, q, message))
        return answers[0]
    except Exception as e:
        return f"Error: {str(e)}"