import argparse
import os

from langchain.chains import ConversationalRetrievalChain, QAGenerationChain
from langchain.chat_models import ChatOpenAI

from app import create_app
from app.index_handler import load_index

import constants
os.environ["OPENAI_API_KEY"] = constants.APIKEY

index = None
chain = None
args = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-3.5-turbo",
                        help="The OpenAI model name")
    parser.add_argument("--persist", default=True, action="store_true",
                        help="Enable to save the model index to disk and reuse it")
    args = parser.parse_args()

    app = create_app()

    # Load the index and create the chain
    index = load_index(args.persist)
    llm = ChatOpenAI(model=args.model)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
        get_chat_history=lambda h: h
    )
    # chain = load_qa_chain(
    #     llm=llm,
    #     #retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    #     chain_type="map_rerank"
    #     #get_chat_history=lambda h: h
    # )
    #Loader = DirectoryLoader('./data')
    #docs = Loader.load()

    # Pass the 'chain' variable in the app's config
    #app.config["docs"] = docs
    app.config["chain"] = chain
    app.run(host="127.0.0.1", port=5000)
