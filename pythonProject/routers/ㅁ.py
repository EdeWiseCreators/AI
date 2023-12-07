from fastapi import APIRouter
from fastapi import Form
from typing_extensions import Annotated
import os
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chains import LLMChain
from langchain import ConversationChain
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from typing import Optional
import json


class Item(BaseModel):
    quiz: str  # 추가된 필드
    subject: str  # 추가된 필드


chatbot = APIRouter(prefix='/chat')

os.environ["OPENAI_API_KEY"] = ""  # 환경변수에 OPENAI_API_KEY를 설정합니다.

loader = PyPDFLoader("D:\myprj\pythonProject\pdf\사회6-1-1-1(교과서).pdf")


def chatmodel(loader):
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(texts, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)  # Modify model_name if you have access to GPT-4

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True)

    return chain


@chatbot.get('/senda')
def sendchat():
    return {"chat": "안녕"}


@chatbot.post('/send', tags=['chat'])
def sendchat_post(text: Annotated[str, Form()]):
    print(text)
    # text = "박정희는 어떤 일을 했어?"
    chain = chatmodel(loader)
    result = chain(text)
    return result["answer"]
    # return text


@chatbot.post('/send2', tags=['chat'])
def sendchat_post2(text: Annotated[str, Form()]):
    print(text)
    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2)

    prompt = PromptTemplate(
        input_variables=["step"],
        template="""Please answer the question in 200 characters or less.
        Keep your tone formal.
        Lastly, please answer in Korean.
        {step}
        """
    )

    chain = LLMChain(llm=chat, prompt=prompt)
    result = chain.run(step=text)

    return result


@chatbot.post('/send_student', tags=['chat'])
def sendchat_post3(text: Annotated[str, Form()]):
    print(text)
    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2)

    prompt = PromptTemplate(
        input_variables=["step"],
        template="""You are 에듀 who helps elementary school students in Korea.
        When elementary school students ask questions, please answer according to the students' level and standards.
        Please answer in the tone of an elementary school student.
        Please answer the question in 200 characters or less.

        Lastly, please answer in Korean.
        {step}
        """
    )

    chain = LLMChain(llm=chat, prompt=prompt)
    result = chain.run(step=text)

    return result


@chatbot.post('/quiz')
def sendchat_quiz(item: Item):
    print(item)
    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

    prompt = PromptTemplate(
        input_variables=["exam", "json_schema"],
        template="""You are an elementary school teacher in South Korea. You need to create a quiz for a subject.
        {exam}
        The answers to all questions are generated in Korean.
        Finally, you respond with the following JSON schema:

        {json_schema}
        """
    )
    # Please create one o,x quiz about {quiz} in the {subject} subject.
    chain = LLMChain(llm=chat, prompt=prompt)

    quiz = item.quiz
    subject = item.subject

    result = chain.run(exam=f"""Please create an OX quiz for {quiz} in the subject {subject}.
    1. Please create only one quiz.
    2. Generate the correct answers for the quiz.
    3. Generate elementary school-aged Commentary to quiz question.""",
                       json_schema="""{
                       "quiz": ,
                       "answer": ,
                       "Commentary" :
                       }""")
    # print(result)
    result_data = json.loads(result)
    print(result_data)

    return result_data

