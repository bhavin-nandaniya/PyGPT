import os

from flask import Blueprint, current_app, request, jsonify, render_template, session

# from langchain.chains import ConversationalRetrievalChain
# from langchain.chat_models import ChatOpenAI
# from langchain.document_loaders import DirectoryLoader
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.indexes.vectorstore import VectorStoreIndexWrapper
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
from langchain.memory import ChatMessageHistory


chat_handler = Blueprint("chat_handler", __name__)

# Function to prepend speaker


def format_chat_message(message, speaker):
    return f"{speaker}: {message}"


# Route to handle API requests
@chat_handler.route("/api/chat", methods=["POST"])
def chat():
    # Parse JSON data from the request
    data = request.json

    # Access the 'chain' variable from the current_app context
    #docs = current_app.config.get("docs")
    chain = current_app.config.get("chain")

    # Get the question and chat history from the request data
    question = data.get("question")
    chat_history = data.get("chat_history", [])

    # Convert the chat history to the desired format
    formatted_chat_history = []
    for user_message, ai_message in chat_history:
        user_formatted = format_chat_message(user_message, 'USER')
        ai_formatted = format_chat_message(ai_message, 'AI')
        formatted_chat_history.append(f"{user_formatted}\n{ai_formatted}")
    
    print(formatted_chat_history)

    # Check if the user wants to quit
    if question in ['quit', 'q', 'exit']:
        return jsonify({"response": "Goodbye!"})

    # Process the question using the chain
    result = chain(
        {"question": question, "chat_history": formatted_chat_history})
    response = result["answer"]
    #response = chain.run({"input_documents": docs[:99], "question": question}, return_only_outputs=True)

    # Append the conversation to the chat history
    chat_history.append((question, response))

    return jsonify({"response": response, "chat_history": chat_history})

# Route to serve the index.html file


@chat_handler.route("/", methods=["GET"])
def index():
    # if session.get('history') is None:
    #     session["history"] = ""
    #  print(f"session: {session['history']}")

    return render_template("index.html")
