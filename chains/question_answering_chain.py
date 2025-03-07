from langchain.chains import RetrievalQA

def answer_question(llm, retriever, question):
    chain = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type="stuff")
    return chain.invoke(question)
