import pandas as pd
import numpy as np
from langchain.docstore.document import Document
from langchain.retrievers import EnsembleRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.retrievers import BM25Retriever
from collections import defaultdict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
import pickle
from langchain.chains import RetrievalQA





def load_chunks_to_pickle(file_path):
    with open(file_path,'rb') as f:
        embedding_with_metadata = pickle.load(f)
    return embedding_with_metadata


#metadata extraction helper functions
def consolidate_metadata(source_documents):
    """
    Consolidates metadata from a list of Document objects, aggregating page numbers by book name.

    Args:
        source_documents (list of Document) - source['documents']: List of Document objects containing metadata and page content from the QA chain output.
            
    Returns:
        str: A formatted string listing book names and their unique page numbers.
    """
    # Consolidate metadata and page numbers
    book_pages = defaultdict(set)
    for doc in source_documents:
        metadata = doc.metadata['metadata']
        if isinstance(metadata, list):
            for meta in metadata:
                book_name = meta['book_name']
                page_number = meta['page_number']
                book_pages[book_name].add(page_number)
        else:
            book_name = metadata['book_name']
            page_number = metadata['page_number']
            book_pages[book_name].add(page_number)

    # Format the output
    consolidated_output = []
    for book_name, pages in book_pages.items():
        pages_list = sorted(list(pages))
        consolidated_output.append(f"Book_name: {book_name}, Page_numbers: {tuple(pages_list)}")

    final_output = " ; ".join(consolidated_output)
    return final_output


# Initialize SentenceTransformer model for embeddings
embd_model = HuggingFaceEmbeddings(model_name='multi-qa-MiniLM-L6-cos-v1')

#Initialize the Milvus vector store 
vectorstore = Milvus(embedding=embd_model,
                    connection_args={"uri":"Milvus_db/milvus_robo_qa.db"},
                    collection_name="robotics_textbooks",
                    )

#initialize the retrievers
#milvus retriever 
milvus_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

#BM25 
documents = load_chunks_to_pickle("documents.pkl")
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 3

#combine the retrievers
ensemble_retriever = EnsembleRetriever(retrievers=[milvus_retriever,bm25_retriever])


#reranking using FlashRank using - "ms-marco-MultiBERT-L-2-v2"
compressor = FlashrankRerank()
compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,base_retriever=ensemble_retriever)



# code for query expansion using stepback prompting
  
def stepback_prompting_expansion(query,api_key):
    """
    The `stepback_prompting_expansion` function paraphrases a user query into a more generic form using few-shot examples and an AI model.

    :param query: The user's input question to be paraphrased.
    :param api_key: The OpenAI API key for authenticating requests.

    :return: A paraphrased, more generic question based on the input query.
    """    
    # Step- back prompting
    examples = [
        {
            "input": "Could the members of The Police perform lawful arrests?",
            "output": "what can the members of The Police do?",
        },
        {
            "input": "Jan Sindel’s was born in what country?",
            "output": "what is Jan Sindel’s personal history?",

            "input" : "Is it possible to get forward kinematics from inverse in robotics?",
            "output": "what is the relationship between forward and inverse kinematics in robotics?",
        },]
    # transform these to example messages
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
        )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert at world knowledge. Your task is to step back and paraphrase a question to a more generic step-back question, which is easier to answer. Here are a few examples:""",
            ),
            # Few shot examples
            few_shot_prompt,
            # New question
            ("user", "{question}"),
        ]
        )

    llm_model = "gpt-4o-mini"
    prompt_model= ChatOpenAI(model_name= llm_model,temperature=0,openai_api_key = api_key)
    question_gen = prompt | prompt_model | StrOutputParser()
    few_shot_ques = question_gen.invoke({"question":query})
    
    return few_shot_ques


def init_QA_chain(api_key):
    """
    The `init_QA_chain` function initializes a question-answering chain using a specified language model and template for robotics questions.

    :param api_key: The OpenAI API key for authenticating requests.

    :return: The initialized question-answering chain.
    """

    llm_model = "gpt-4o-mini"
    QA_llm = ChatOpenAI(model_name= llm_model,temperature=0,openai_api_key =api_key)

    # question answering template
    QA_template = """Answer the question about the field of robotics based only on the given context.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    :
    {context}
    Question: {question}
    Answer:"""

    #qa chain prompt
    QA_chain_prompt = PromptTemplate.from_template(QA_template)
    
    #define the QA chain
    QA_chain = RetrievalQA.from_chain_type(QA_llm,retriever= compression_retriever,
                                       return_source_documents=True, verbose=False,
                                     chain_type_kwargs={"prompt":QA_chain_prompt})
    return QA_chain

def make_output(query,api_key):
    """
    The `make_output` function expands a query, invokes a QA chain, and returns the result along with consolidated metadata.

    :param query: The user-provided search query or question.
    :param api_key: The OpenAI API key for authentication.

    :return: The result and metadata from the QA chain.
    """

   
    expanded_query = stepback_prompting_expansion(query,api_key)
    
    QA_chain = init_QA_chain(api_key)
    
    answer = QA_chain.invoke({"query": expanded_query})
    
    result = answer["result"]
    
    metadata = consolidate_metadata(answer["documents"])
    
    return result, metadata