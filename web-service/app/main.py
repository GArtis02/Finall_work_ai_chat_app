from fastapi import FastAPI
from pydantic import BaseModel
import openai
import random
import json
import time
import config
import functions 

function.Profession_info()
app = FastAPI()

# add key
openai.api_key = config.OPENAI_API_KEY


# Model for a single message
class Message(BaseModel):
    role: str
    content: str


def Profession_info(OriginalPromth):
    result = functions.Profession_info(OriginalPromth)
    return

def vacancies_info(OriginalPromth):
    result = functions.vacancies_info(OriginalPromth)
    return


# Define the custom tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "Profession_info",
            "description": "Return information abouth a profesion, how much they work, earn and similar",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vacancies_info",
            "description": "Returns information abouth free vacancies in the workmarket",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# 40-mini is the cheapest one.
assistant = openai.beta.assistants.create(
    name="Custom Tool Assistant",
    instructions="You are an assistant with access to custom tools that returns information abouth open vacansies and information abouth Professions.",
    model="gpt-4o-mini",
    tools=tools
)

# Route to receive and process a user message
@app.post("/send-message/")
async def process_message_and_respond(thread_id: str, message: str):
    """
    Receive a message from the user and return a response from the virtual assistant.

    Args:
        thread_id (str): The ID of the conversation thread.
        message (str): The message sent by the user.

    Returns:
        dict: A dictionary containing the thread ID, the assistant's response, and the original message.
    """
    
    # Create a new thread for the conversation if not already present
    thread = openai.beta.threads.create()
    
    # Add the received message to the conversation thread
    user_message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    
    # Run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Poll for the assistant's response
    attempt = 1
    while run.status != "completed":
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "requires_action":
            break
        attempt += 1
        time.sleep(2)
    
    # If the assistant requests to use a tool
    if run.status == "requires_action":
        if run.required_action:
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.function.name == "Profession_info":
                    output = Profession_info(message)
                elif tool_call.function.name == "vacancies_info":
                    output = vacancies_info(message)
                else:
                    output = "Unknown tool"
                
                # Submit the tool's result back to the assistant
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": str(output)
                    }]
                )
    
    # Wait for the assistant to complete the run after using the tool
    run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    attempt = 1
    while run.status not in ["completed", "failed"]:
        time.sleep(2)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        attempt += 1
    
    # Retrieve the assistant's final response
    if run.status == "completed":
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        final_answer = messages.data[0].content[0].text.value
        return {
            "thread_id": thread_id,
            "response": final_answer,
            "message_received": message
        }
    else:
        return {
            "thread_id": thread_id,
            "response": "The assistant failed to complete the request.",
            "message_received": message
        }


# Retrieve a conversation history based on the thread ID, 5 messages from the user, 5 from the assistant
@app.get("/conversation-history/")
async def conversation_history(thread_id: str):
    """
    Retrieve the conversation history for a specific thread.

    Args:
        thread_id (str): The ID of the conversation thread.

    Returns:
        dict: A dictionary containing the thread ID and a list of conversation messages, including both user and assistant messages.
    """
    
    # Fill the message history with dummy messages
    user_messages = [f"User message {i} in thread {thread_id}" for i in range(1, 6)]
    assistant_messages = [f"Assistant message {i} in thread {thread_id}" for i in range(1, 6)]
    conversation_history = []
    for i in range(5):
        conversation_history.append({"sender": "user", "content": user_messages[i]})
        conversation_history.append({"sender": "assistant", "content": assistant_messages[i]})

    return {
        "thread_id": thread_id,
        "conversation_history": conversation_history
    }