import config
import openai
import random
import json

def Profession_info(OriginalPromth):
    openai.api_key = config.OPENAI_API_KEY
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

    message_Pased = OriginalPromth

    # User message
    messages = [{"role": "user", "content": message_Pased}]
    profession_queries = {}

    try:
        # Try making the API call
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="required"
        )
        
        # Extract tool calls
        tool_calls = completion.choices[0].message.tool_calls

        # Check if tool calls exist
        if tool_calls:
            # Loop through each tool call
            for idx, tool_call in enumerate(tool_calls):
                function = tool_call.function
                if function:
                    # Try parsing JSON arguments
                    try:
                        arguments = json.loads(function.arguments)
                        profession_name = arguments['profession_name']
                        query = arguments['query']
                        
                        # Add to dictionary
                        if profession_name not in profession_queries:
                            profession_queries[profession_name] = []
                        
                        profession_queries[profession_name].append(query)
                    
                    except json.JSONDecodeError:
                        error_message = "Error: Failed to parse function arguments."
                        return {"data": None, "error": error_message}
        
            # Output results if profession_queries has data
            if not profession_queries:
                error_message = "No data could be extracted from the tool calls."
                return {"data": None, "error": error_message}
        
        else:
            error_message = "No tool calls found. The query may not match the tool's capabilities."
            return {"data": None, "error": error_message}
            
    except openai.error.OpenAIError as e:
        error_message = f"An error occurred with the OpenAI API: {e}"
        return {"data": None, "error": error_message}
    
    # Return data if no error occurred
    return {"data": profession_queries, "error": None}


def vacancies_info(OriginalPromth):
    openai.api_key = config.OPENAI_API_KEY
    tools = [
        {
            "type": "function",
            "function": {
                "name": "vacancies_info",
                "description": "Return information about a profession in Latvian from users message, that will be used to search for vacancies in a DB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Search_value_profesion": {
                            "type": "string",
                            "description": "The search value used for vacancy profession in Latvian"
                        },
                        "Search_term": {
                            "type": ["string", "null"],
                            "description": "Search parameter about the vacancy in Latvian",
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
                            "description": "Search value for Search_term about the vacancy in Latvian",
                        }
                    },
                    "additionalProperties": False,
                    "required": ["Search_value_profesion", "Search_term", "Search_value_for_term"]
                }
            }
        }
    ]

    message_Pased = OriginalPromth
    messages = [{"role": "user", "content": message_Pased}]
    vacancies_queries = {}

    try:
        # API call
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="required"
        )
        
        # Extract tool calls
        tool_calls = completion.choices[0].message.tool_calls

        if tool_calls:
            # Parse each tool call
            for idx, tool_call in enumerate(tool_calls):
                function = tool_call.function
                if function:
                    # Try parsing JSON arguments
                    try:
                        arguments = json.loads(function.arguments)
                        search_value_profesion = arguments['Search_value_profesion']
                        search_term = arguments['Search_term']
                        search_value_for_term = arguments['Search_value_for_term']
                        
                        # Add to dictionary
                        if search_value_profesion not in vacancies_queries:
                            vacancies_queries[search_value_profesion] = []
                        
                        vacancies_queries[search_value_profesion].append({
                            "term": search_term,
                            "value": search_value_for_term
                        })
                    
                    except json.JSONDecodeError:
                        error_message = "Error: Failed to parse function arguments."
                        return {"data": None, "error": error_message}

            # Check if data was extracted
            if not vacancies_queries:
                error_message = "No data could be extracted from the tool calls."
                return {"data": None, "error": error_message}
        
        else:
            error_message = "No tool calls found. The query may not match the tool's capabilities."
            return {"data": None, "error": error_message}
            
    except openai.OpenAIError as e:
        error_message = f"An error occurred with the OpenAI API: {e}"
        return {"data": None, "error": error_message}
    
    # Return extracted data
    return {"data": vacancies_queries, "error": None}
    