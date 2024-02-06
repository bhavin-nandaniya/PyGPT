import threading
import signal
import os

from flask import Blueprint, request, jsonify, render_template
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

index_handler = Blueprint("index_handler", __name__)

# Function to load the index from the directory
def load_index(persist):
    if persist and os.path.exists("persist"):
        print("Reusing index...\n")
        vectorStore = Chroma(persist_directory="persist",embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorStore)
    else:
        loader = DirectoryLoader("./data/")
        print("Loading from: \n")
        print(loader)
        print("\n-----------------------")
        if persist:
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader])
        else:
            index = VectorstoreIndexCreator().from_loaders([loader])
    return index

# Additional routes or handlers related to index management
# ...
