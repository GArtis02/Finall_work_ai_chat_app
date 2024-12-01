import openai
import json
from openai import OpenAIError
# web-service\web-service-env\Lib\site-packages\functions.py location for file after git
# Profession Info function

# add key here
#openai.api_key = 

def Profession_info(original_prompt):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "profession_info",
                "description": "Return information about a profession in Latvian from users message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "profession_name": {
                            "type": "string",
                            "description": "The name of the profession in Latvian"
                        },
                        "query": {
                            "type": ["string", "null"],
                            "description": "What the user wants to know about the profession in Latvian",
                            "enum": [
                                "Nostrādātās stundas",
                                "Vidējais darba stundu skaits mēnesī vienai darba vietai",
                                "Ienākumi kopā, EUR",
                                "Vidējā stundas tarifa likme, EUR",
                                "Darba vietu skaits"
                            ]
                        }
                    },
                    "additionalProperties": False,
                    "required": ["profession_name", "query"]
                }
            }
        }
    ]

    messages = [{"role": "user", "content": original_prompt}]
    profession_queries = {}

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        tool_calls = completion.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                function = tool_call.function
                arguments = json.loads(function.arguments)
                profession_name = arguments['profession_name']
                query = arguments['query']

                if profession_name not in profession_queries:
                    profession_queries[profession_name] = []
                profession_queries[profession_name].append(query)
        else:
            return {"data": None, "error": "No tool calls found."}
    except openai.error.OpenAIError as e:
        return {"data": None, "error": str(e)}

    return {"data": profession_queries, "error": None}

# Vacancies Info function
def vacancies_info(original_prompt):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "vacancies_info",
                "description": "Return information about vacancies from a user prompt in Latvian.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Search_value_profesion": {
                            "type": "string",
                            "description": "Search value for the vacancy in Latvian"
                        },
                        "Search_term": {
                            "type": ["string", "null"],
                            "description": "Search term about the vacancy in Latvian",
                            "enum": [
                                "Vakances kategorija",
                                "Alga",
                                "Slodzes tips",
                                "Darba stundas nedēļā",
                                "Vieta"
                            ]
                        },
                        "Search_value_for_term": {
                            "type": ["string", "null"],
                            "description": "Search value for the given search term",
                        }
                    },
                    "additionalProperties": False,
                    "required": ["Search_value_profesion", "Search_term", "Search_value_for_term"]
                }
            }
        }
    ]

    messages = [{"role": "user", "content": original_prompt}]
    vacancies_queries = {}

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        tool_calls = completion.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                function = tool_call.function
                arguments = json.loads(function.arguments)
                search_value_profesion = arguments['Search_value_profesion']
                search_term = arguments['Search_term']
                search_value_for_term = arguments['Search_value_for_term']

                if search_value_profesion not in vacancies_queries:
                    vacancies_queries[search_value_profesion] = []
                vacancies_queries[search_value_profesion].append({
                    "term": search_term,
                    "value": search_value_for_term
                })
        else:
            return {"data": None, "error": "No tool calls found."}
    except openai.error.OpenAIError as e:
        return {"data": None, "error": str(e)}

    return {"data": vacancies_queries, "error": None}
