import openai
import json
import config
openai.api_key = config.OPENAI_API_KEY

tools = [
    {
        "type": "function",
        "function": {
            "name": "vacancies-info",
            "description": "Return information about a profession in Latvian from users message, that will be used to search for vacancies in a DB",
            "parameters": {
                "type": "object",
                "properties": {
                    "Search_value_profesion": {
                        "type": "string",
                        "description": "The search value used for vacancie profession in Latvian"
                    },
                    "Search_term": {
                        "type": ["string", "null"],
                        "description": "Search parameter about the vacancie in Latvian",
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
                        "description": "Search value for Search_term about the vacancie in Latvian",
                    }
                },
                "additionalProperties": False,
                "required": ["Search_value_profesion", "Search_term", "Search_value_for_term"]
            }
        }
    }
]

message_Pased = "Tell me abouth vacancies in Riga, for kitchen workers and hotell manager, and how much does the latter one earn?"

# User message
messages = [{"role": "user", "content": message_Pased}]

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
    vacancies_queries = {}

    # Check if tool calls exist
    if tool_calls:
        # Loop through each tool call
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
                    print("Error: Failed to parse function arguments.")
    
        # Output results if vacancies_queries has data
        if vacancies_queries:
            for profession, details in vacancies_queries.items():
                print(f"Profession: {profession}")
                for i, detail in enumerate(details, start=1):
                    print(f"  {i}. {detail['term']}: {detail['value']}")
        else:
            print("No data could be extracted from the tool calls.")
    
    else:
        print("No tool calls found. The query may not match the tool's capabilities.")
        
except openai.OpenAIError as e:
    print("An error occurred with the OpenAI API:", e)
    
    
