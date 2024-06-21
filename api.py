DATABRICKS_HOST = "<DATABRICKS_HOST>"
DATABRICKS_TOKEN = "<DATABRICKS_TOKEN>"
VS_ENDPOINT = "<VS_ENDPOINT>"
VS_INDEX = "<VS_INDEX>"

from langchain_core.prompts import ChatPromptTemplate

template = """
Act as a California winery visit expert for visitors to California wine country who want an incredible visit and tasting experience. 
You are a personal visit assistant named Databrick's CA Wine Country Visit Assistant. 
Provide the most accurate information on California wineries based on brochures of different wineries provided to you in the context. 
Only provide information if there is an exact match in the context. 
Do not go outside of the information provided to you in the context at all. 
Do not make anything up. Information should be 100 percent from that text. 
Do not infer anything at all.

Context: {context}
Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(template)


from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores.databricks_vector_search import DatabricksVectorSearch
from databricks.vector_search.client import VectorSearchClient
from langchain_openai import ChatOpenAI


vsc = VectorSearchClient(workspace_url=DATABRICKS_HOST, personal_access_token=DATABRICKS_TOKEN, disable_notice=True)
index = vsc.get_index(endpoint_name=VS_ENDPOINT, index_name=VS_INDEX)
db = DatabricksVectorSearch(index=index, columns=["_file", "_modified", "_fivetran_synced", "_chunk_index", "_chunk"])


def get_answer(use_context, model, question):
    llm = ChatOpenAI(api_key=DATABRICKS_TOKEN,base_url=f"{DATABRICKS_HOST}/serving-endpoints", model=model)
    if use_context:
        inputs = {"context": db.as_retriever(), "question": RunnablePassthrough()}
        rag_chain = (inputs | prompt | llm | StrOutputParser())
    else:
        rag_chain = (RunnablePassthrough() | llm | StrOutputParser())

    return rag_chain.invoke(question)