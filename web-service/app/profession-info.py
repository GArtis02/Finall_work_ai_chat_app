# profession_tool.py
import openai
import json
import sys  # Import sys to allow printing to stderr

# add key here
#openai.api_key = 


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

message_Pased = "Tell me how much money does a doctor, game designer make in a year and how many open jobs are there?"

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
    profession_queries = {}

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
                    print("Error: Failed to parse function arguments.")
    
        # Output results if profession_queries has data
        if profession_queries:
            for profession, queries in profession_queries.items():
                print(f"Profession: {profession}")
                for i, query in enumerate(queries, start=1):
                    print(f"  {i}. {query}")
        else:
            print("No data could be extracted from the tool calls.")
    
    else:
        print("No tool calls found. The query may not match the tool's capabilities.")
        
except openai.error.OpenAIError as e:
    print("An error occurred with the OpenAI API:", e)
    
