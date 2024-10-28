# @title Noklusējuma nosaukuma teksts
import json
import openai
import random
import os
import time
import config
# Set your OpenAI API key
# this key has auto-charge disabled, no billing methog assigned, and 5$ in API credits.
# Ideally, you should use your own OpenAI account, and your own money

openai.api_key = config.OPENAI_API_KEY
# Define the custom tools
tools = [
    {   
        "type": "function",
            "function": {
            "name": "profession_info",
            "description": "Return information about a profession in Latvian",
            "parameters": {
                "type": "object",
                "required": ["profession_name", "query"],
                "properties": {
                    "profession_name": {
                        "type": "string",
                        "description": "The name of the profession in Latvian"
                    },
                    "query": {
                        "type": "string",
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
                "additionalProperties": False
            }
        }
    }
]

# 40-mini is the cheapest one.
assistant = openai.beta.assistants.create(
    name="Custom Tool Assistant",
    instructions="You are an assistant with access to custom tool that returns profession info.",
    model="gpt-4o-mini",
    tools=tools
)

print(f"Assistant created with ID: {assistant.id}")

# Define the tool functions
def profession_info():
    return

# Create a conversation thread
thread = openai.beta.threads.create()
print(f"Thread created with ID: {thread.id}")

# Add a message to the thread
print("Submitting your query to assistant")
message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I would like to know the total income of a chef in a year"
)

# Run the assistant
run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Wait for the run to complete
attempt = 1
while run.status != "completed":
    print(f"Run status: {run.status}, attempt: {attempt}")
    run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action":
        break

    attempt += 1
    time.sleep(2)

# status "requires_action" means that the assistant decided it needs to call an external tool
# assistant gives us names of tools it needs, we call the corresponding function and return the data back to the assistant
if run.status == "requires_action":
    print("Run requires action, assistant wants to use a tool")

    # Process tool calls
    if run.required_action:
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "profession_info":
                print("  profession_info called")
                output = profession_info()
            else:
                print("Unknown function call")
            print(f"  Generated output: {output}")

            # submit the output back to assistant
            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[{
                    "tool_call_id": tool_call.id,
                    "output": str(output)
                }]
            )

print("Submitting tool results to assistant")
if run.status == "requires_action":

    # After submitting tool outputs, we need to wait for the run to complete, again
    run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    attempt = 1
    while run.status not in ["completed", "failed"]:
        print(f"Run status: {run.status}, attempt: {attempt}")
        time.sleep(2)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        attempt += 1

if run.status == "completed":
    # Retrieve and print the assistant's response
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    final_answer = messages.data[0].content[0].text.value
    print(f"=========\n{final_answer}")
elif run.status == "failed":
    print("The run failed. Please check the error messages.")
else:
    print(f"Unexpected run status: {run.status}")