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
    user_query = "Find jobs in Rīga in Transports / Loģistika."
    extracted_data = extract_search_params_dynamically(user_query)

    # Load the data (replace with your data file path)
    with open("web-service/app/vakances_cleaned_enriched.json", "r", encoding="utf-8") as f:
        all_vacancies = json.load(f)

    # Preprocess vacancies
    preprocessed_vacancies = preprocess_vacancies(all_vacancies)

    # Filter the vacancies
    filtered_list = filter_vacancies(preprocessed_vacancies, extracted_data)

    # Get the final response
    final_answer = create_final_response(filtered_list)
    print("Final Answer:", final_answer)
