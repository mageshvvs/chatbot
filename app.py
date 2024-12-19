from flask import Flask, request, jsonify, render_template, session
import requests

app = Flask(__name__)
app.secret_key = "7qCUMYqHxt0FK6AA"  # Required for session management

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Add your API key securely (never hardcode in production)
API_KEY = "sk-proj-BjxekZt6FbANKcXaVplBKCyXrryg_j7PfXT3BlbkFJBYWpSUKLNGlQNKUFeAYk8RjgDnE3z37Ja9hetc3XdCBvLnBGqz-BPXnetQ7qCUMYqHxt0FK6AA"  # Required for session management

@app.route('/')
def index():
    # Render the HTML page
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Add company-specific context
    context = """
    You are a company chatbot for SuruG Tech LLC, an IT job consulting company.
    mandator: you need to get candidate name details worexperience and assess candidate by asking relavent questions.
    Here is the relevant company information:
    - Company Name: SuruG Tech LLC
    - Type: IT Job Consulting Company
    - Available Jobs: Java Microservices job with 7 years of experience
    - Business Hours: Monday to Friday, 9 AM to 5 PM CST
    - Contact Info: gopika@surugtech.com, +1-469-427-5382
    - CEO: Gopika Ganesan
    - Bench Sales team member: Magesh VVS
    - Company operates from Mckinney Texas
    
    without fail ask candiate name details qualification and also ask atleaet 5 interview questions related to micro service and java
    Also Respond to user queries based on this information and provide concise, accurate answers.
    """

    # Get user input from the request
    data = request.json
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"error": "Missing 'message' in the request"}), 400

    # Initialize chat history in session if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = [{"role": "system", "content": context}]
    
    # Add user message to the chat history
    session['chat_history'].append({"role": "user", "content": user_message})
    
    # Prepare OpenAI API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4",  # Ensure you are using the correct model
        "messages": session['chat_history'],
        "temperature": 0.7
    }
    
    # Make API call to OpenAI
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        response_data = response.json()
        
        # Extract assistant message
        assistant_message = response_data["choices"][0]["message"]["content"]
        
        # Add assistant message to the chat history
        session['chat_history'].append({"role": "assistant", "content": assistant_message})
        
        return jsonify({"response": assistant_message})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {e}"}), 500
    except KeyError:
        return jsonify({"error": "Unexpected response format from OpenAI"}), 500

@app.route('/reset', methods=['POST'])
def reset_chat():
    # Clear the chat history
    session.pop('chat_history', None)
    return jsonify({"message": "Chat history reset successful."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
