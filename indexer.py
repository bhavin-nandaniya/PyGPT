import os

import constants  # For our API Key

from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import DirectoryLoader, GoogleDriveLoader, UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# loader = TextLoader('data.txt')
# Loader = DirectoryLoader('./data')
Loader = GoogleDriveLoader(folder_id="1KGxL3l_RERlC4dV-Fpw9gc-ZabwCp54I",
                           credentials_path="./configs/gcredsDesktop.json", token_path="./configs/token.json")

print("-------- Vectorstore Indexer Started --------")
index = VectorstoreIndexCreator(
    vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([Loader])
print("-------- Vectorstore Indexer Ended --------")
