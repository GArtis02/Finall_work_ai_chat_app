from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

import json
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "vakances_cleaned_enriched.json")

# Configure the logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),  # File handler with UTF-8 encoding
        logging.StreamHandler(sys.stdout)  # Stream handler
    ]
)

app = FastAPI()

# Endpoint models
class JobQuery(BaseModel):
    query: str

# Global variable for vacancies
all_vacancies = []

# Load and preprocess vacancies on startup
@app.on_event("startup")
async def load_vacancies():
    global all_vacancies
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            all_vacancies = preprocess_vacancies(json.load(f))
        logging.info(f"Vacancies loaded and preprocessed successfully. Total: {len(all_vacancies)}")
        # logging.error(f,all_vacancies)
    except Exception as e:
        logging.error(f"Error loading vacancies: {e}")
        all_vacancies = []
        # logging.error(f,all_vacancies)

# API endpoint to filter job vacancies based on query
@app.post("/filter-vacancies/")
async def filter_job_vacancies(job_query: JobQuery):
    try:
        # Extract search parameters from user query
        extracted_params = extract_search_params_dynamically(job_query.query)
        logging.info(f"Extracted search parameters: {extracted_params}")

        # Filter the vacancies
        filtered_vacancies = filter_vacancies(all_vacancies, extracted_params)
        logging.info(f"Filtered {len(filtered_vacancies)} vacancies from the dataset.")

        # Create a final response
        final_response = create_final_response(filtered_vacancies)
        return {"query": job_query.query, "response": final_response}
    except Exception as e:
        logging.error(f"Error processing the job query: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the job query.")

# API endpoint to handle sending messages
@app.get("/send-message/")
async def send_message(thread_id: int, message: str):
    try:
        logging.info(f"Message received for thread {thread_id}: {message}")

        if not thread_id or not isinstance(thread_id, int):
            logging.error("Invalid thread_id provided.")
            raise HTTPException(status_code=400, detail="Invalid thread_id.")
        
        if not message.strip():
            logging.error("Empty message received.")
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Extract search parameters
        extracted_params = extract_search_params_dynamically(message)
        logging.debug(f"Extracted parameters: {extracted_params}")

        if not extracted_params:
            logging.warning("No search parameters extracted.")
            return {
                "status": "error",
                "message": "Could not extract search parameters. Check message format.",
                "filtered_vacancies": [],
            }

        # Filter vacancies
        logging.debug(f"All vacancies dataset size: {len(all_vacancies)}")
        filtered_vacancies = filter_vacancies(all_vacancies, extracted_params)
        logging.info(f"Filtered {len(filtered_vacancies)} vacancies.")

        if not filtered_vacancies:
            logging.info("No vacancies matched the criteria.")
            response = {
                "status": "success",
                "thread_id": thread_id,
                "original_message": message,
                "response": "Nav atrastas vakances",
            }
            logging.debug(f"Response payload: {response}")
            return response

        # Create response
        final_response = create_final_response(filtered_vacancies)
        response = {
            "status": "success",
            "thread_id": thread_id,
            "original_message": message,
            "response": final_response,  # Use 'response' as the key for consistency

        }
        logging.debug(f"Response payload: {response}")

        return response

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


import json
from fuzzywuzzy import fuzz

# Function to extract search parameters dynamically
def extract_search_params_dynamically(user_query):
    import openai
    openai.api_key = ""

    prompt = f"""
    The following is a user's job-related query: "{user_query}"

    Please extract the following information if available, and return a JSON object in Latvian language:
    - location: The city or region (string)
    - category: The job category or industry (string)
    - salary_from: The minimum salary mentioned (number)
    - salary_to: The maximum salary mentioned (number)
    - keywords: A list of any additional relevant keywords mentioned in the query

    Only include keys for fields that are present in the query. If a field isn't mentioned, do not include it.

    The output should be strictly JSON with no extra text.
    Example:
    {{
      "location": "Riga",
      "salary_from": 1000,
      "salary_to": 2000
    }}
    """
    
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message.content.strip()

    # Clean code blocks if present
    if response.startswith("```") and response.endswith("```"):
        response = response.split("\n", 1)[1].rsplit("\n", 1)[0]

    # Parse JSON
    extracted_params = json.loads(response)
    return extracted_params

# Preprocess vacancies to handle null values
def preprocess_vacancies(vacancies):
    for v in vacancies:
        # Ensure all keys are present and lowercase values only if they are not None
        v["Location"] = v.get("Location", "").lower() if v.get("Location") is not None else ""
        v["Category"] = v.get("Category", "").lower() if v.get("Category") is not None else ""
        v["Salary From (EUR)"] = v.get("Salary From (EUR)", 0) if v.get("Salary From (EUR)") is not None else 0
        v["Salary To (EUR)"] = v.get("Salary To (EUR)", float("inf")) if v.get("Salary To (EUR)") is not None else float("inf")
        v["Workload Type"] = v.get("Workload Type", "").lower() if v.get("Workload Type") is not None else ""
        v["Work Schedule"] = v.get("Work Schedule", "").lower() if v.get("Work Schedule") is not None else ""
    return vacancies

# Function to filter vacancies
def filter_vacancies(vacancies, params):
    def matches_criteria(v):
        # Location match
        if "location" in params:
            if "Location" not in v or fuzz.partial_ratio(v["Location"].lower(), params["location"].lower()) <= 80:
                return False
        
        # Category match
        if "category" in params:
            if "Category" not in v or params["category"].lower() not in v["Category"].lower():
                return False
        
        # Salary match
        if "salary_from" in params:
            sf = params["salary_from"]
            if not (
                ("Salary From (EUR)" in v and v["Salary From (EUR)"] and v["Salary From (EUR)"] >= sf) or
                ("Salary To (EUR)" in v and v["Salary To (EUR)"] and v["Salary To (EUR)"] >= sf)
            ):
                return False
        if "salary_to" in params:
            st = params["salary_to"]
            if not (
                ("Salary From (EUR)" in v and v["Salary From (EUR)"] and v["Salary From (EUR)"] <= st) or
                ("Salary To (EUR)" in v and v["Salary To (EUR)"] and v["Salary To (EUR)"] <= st)
            ):
                return False
        
        # Keyword match
        if "keywords" in params:
            keywords = [kw.lower() for kw in params["keywords"]]
            text_to_search = (
                (v.get("Job Title", "") + " " + v.get("Description", "")).lower()
            )
            if not any(kw in text_to_search for kw in keywords):
                return False
        
        # Workload type
        if "workload_type" in params:
            if "Workload Type" not in v or params["workload_type"].lower() not in v["Workload Type"].lower():
                return False
        
        # Work schedule
        if "work_schedule" in params:
            if "Work Schedule" not in v or params["work_schedule"].lower() not in v["Work Schedule"].lower():
                return False
        
        return True
    
    return [v for v in vacancies if matches_criteria(v)]

# Function to create a final response
def create_final_response(filtered_vacancies):
    """
    Use OpenAI to form a final response based on the filtered vacancies.
    The response might summarize the number of found vacancies and list some details.
    """
    import openai
    openai.api_key = ""


    # Create a prompt with the filtered results
    prompt = f"""
    The user requested job vacancies and we filtered them down as follows:
    {json.dumps(filtered_vacancies, ensure_ascii=False, indent=2)}

    Please provide a helpful response in Latvian summarizing the available job postings.
    If there are too many, just provide a short summary and the count.
    """
    
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content.strip()

# Example usage
if __name__ == "__main__":
    # User query example
    user_query = "Find jobs with pay higher then 500."
    extracted_data = extract_search_params_dynamically(user_query)

    # Load the data (replace with your data file path)
    with open("vakances_cleaned_enriched.json", "r", encoding="utf-8") as f:
        all_vacancies = json.load(f)

    # Preprocess vacancies
    preprocessed_vacancies = preprocess_vacancies(all_vacancies)

    # Filter the vacancies
    filtered_list = filter_vacancies(preprocessed_vacancies, extracted_data)

    # Get the final response
    final_answer = create_final_response(filtered_list)
    print("Final Answer:", final_answer)
