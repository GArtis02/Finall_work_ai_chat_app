## Purpose
This project is a FastAPI-based backend service designed to filter job vacancies based on user queries. It leverages OpenAI's GPT models for dynamic query parameter extraction and fuzzy matching techniques for improved search accuracy.

## Example 
    "query": "Find jobs with pay higher than 1000 in Riga.",
    "response": "Atrastas 5 vakances Rīgā ar algu virs 1000 EUR."

## Project structure
```
web-service/
│
├── app/
│   ├── __init__.py
│   ├── main.py         # Main web service file
│   └── vakances_cleaned_enriched.json      # Stored vacancies 
│
├── .gitignore          # Add filenames you do not want to be added to your repository here
├── requirements.txt    # Dependencies
└── README.md           # The file you are reading right now :)
```

### Activate environment
Linux:  
```
source your_environment_name/bin/activate
```

Windows:  
```
your_environment_name\Scripts\activate
```

# .gitignore file
Add your environment folder, and `/app/__pycache__/` to the project .gitignore file. Contents of these folders should not be committed to your repository.

### Start the app
```
uvicorn app.main:app --reload
```
In this example, app is the folder, main is the filename, and app is used inside main.py.

### Explore the documentation of your web service
Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to see the automatically generated API documentation from FastAPI. You will be able to test the two endpoints (/send_message/ and /conversation_history/) directly from the browser.
If you are using ngrok or Replit or GitPod or some other tool for hosting or tunneling, the link will be different.

## (Optional) make the web service available on the internet
A locally hosted client will easily be able to use a locally hosted web service, but a mobile app will not be able to (localhost is not available on your phone!).
This step is important for those who will use Expo to build their mobile app.

### Install ngrok
[https://ngrok.com/](https://ngrok.com/)

### Use ngrok
This command will create a tunnel from your locally hosted web service (and the specific port!), and make it available online via a temporary URL (for example, https://ab12-a1-ab1-ab1-a1.ngrok-free.app ).
```
ngrok http http://localhost:8000
```
This is useful for development/testing on a small team.
