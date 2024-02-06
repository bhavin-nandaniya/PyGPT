import os
import argparse
import threading
import signal
from flask import Flask, request, jsonify, render_template

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

import constants
os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Function to load the index from the directory
def load_index(persist):
    if persist and os.path.exists("persist"):
        print("Reusing index...\n")
        vectorStore = Chroma(persist_directory="persist",embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorStore)
    else:
        loader = DirectoryLoader("./data/")
        if persist:
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader])
        else:
            index = VectorstoreIndexCreator().from_loaders([loader])
    return index

# Function to reload the index from the directory every 30 minutes
def reload_index_periodically(interval):
    threading.Timer(interval, reload_index_periodically, args=[interval]).start()
    print("Reloading index...")
    global index
    index = load_index(args.persist)
    # Update the chain to use the new index
    global chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model=args.model),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )
    print("Index reloaded successfully!")

def signal_handler(sig, frame):
    print("\nExiting...")
    # Stop the reload thread gracefully
    threading.Timer(1, os._exit, args=[0]).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-3.5-turbo", help="The OpenAI model name")
    parser.add_argument("--persist", default=True, action="store_true", help="Enable to save the model index to disk and reuse it")
    args = parser.parse_args()

    # Load the index and create the chain
    index = load_index(args.persist)
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model=args.model),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    # Start the Flask app
    app = Flask(__name__,template_folder="app/templates")

    # Route to handle API requests
    @app.route("/api/chat", methods=["POST"])
    def chat():
        # Parse JSON data from the request
        data = request.json

        # Get the question and chat history from the request data
        question = data.get("question")
        chat_history = data.get("chat_history", [])

        # Check if the user wants to quit
        if question in ['quit', 'q', 'exit']:
            return jsonify({"response": "Goodbye!"})

        # Process the question using the chain
        result = chain({"question": question, "chat_history": chat_history})
        response = result["answer"]

        # Append the conversation to the chat history
        chat_history.append((question, response))

        return jsonify({"response": response, "chat_history": chat_history})
    
    # Route to serve the index.html file
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # Reload the index from the directory every 30 minutes
    reload_interval_minutes = 1
    reload_interval_seconds = reload_interval_minutes * 60
    threading.Timer(reload_interval_seconds, reload_index_periodically, args=[reload_interval_seconds]).start()

    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Start the Flask app
    app.run(host="127.0.0.1", port=5000)
