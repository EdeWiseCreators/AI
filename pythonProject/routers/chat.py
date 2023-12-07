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
import sqlite3
from collections import Counter
import asyncio
import openai
class Item(BaseModel):
    quiz: str  # 추가된 필드
    subject: str  # 추가된 필드

chatbot = APIRouter(prefix='/chat')
openai.api_key = ''
os.environ["OPENAI_API_KEY"] = "" # 환경변수에 OPENAI_API_KEY를 설정합니다.

# loader = PyPDFLoader("D:\myprj\pythonProject\pdf\사회6-1-1-1(교과서).pdf")

async def chatmodel(loader):
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
        retriever = retriever,
        return_source_documents=True)

    return chain

@chatbot.get('/senda')
async def sendchat():
    return {"chat":"안녕"}

@chatbot.post('/send', tags=['chat'])
async def sendchat_post(text:Annotated[str, Form()]):
    print(text)
    # text = "박정희는 어떤 일을 했어?"
    chain = chatmodel(loader)
    result = chain(text)
    return result["answer"]
    # return text

@chatbot.post('/send2', tags=['chat'])
async def sendchat_post2(text:Annotated[str, Form()]):
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
    
async def async_generate(chain, text):
    resp = await chain.arun(step=text)
    return resp

@chatbot.post('/send_student', tags=['chat'])
async def sendchat_post3(text:Annotated[str, Form()]):
    try:
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
        resp = await asyncio.wait_for(async_generate(chain, text), timeout=30)
        # result = await asyncio.wait_for(chain.run(step=text), timeout=30)  # 30초 타임아웃 설정
        # print(result)
        print(resp)
        print(type(resp))
        # return result
        return resp

    except asyncio.TimeoutError:
        return "다시 질문해주세요"  # 타임아웃 예외 처리


# # 테이블 생성 (처음 한 번만 실행)
# async def create_table():
#     conn = db_connect()
#     conn.execute('''CREATE TABLE IF NOT EXISTS chats (text TEXT)''')
#     conn.commit()
#     conn.close()

# create_table()

# @chatbot.post('/send_student', tags=['chat'])
# async def sendchat_post3(text:Annotated[str, Form()]):
#     # 받은 텍스트를 디비에 저장
#     conn = db_connect()
#     conn.execute('INSERT INTO chats (text) VALUES (?)', (text,))
#     conn.commit()
#     conn.close()
#     print(text)
#     chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2)

#     prompt = PromptTemplate(
#         input_variables=["step"],
#         template="""You are 에듀 who helps elementary school students in Korea.
#         When elementary school students ask questions, please answer according to the students' level and standards.
#         Please answer in the tone of an elementary school student.
#         Please answer the question in 200 characters or less.

#         Lastly, please answer in Korean.
        
#         {step}
#         """
#     )

#     chain = LLMChain(llm=chat, prompt=prompt)
#     result = chain.run(step=text)

#     return result

# # 데이터베이스 연결 설정
# async def db_connect2():
#     return sqlite3.connect('chat_database.db')

# # 데이터베이스 연결 설정 및 테이블 생성 코드는 그대로 유지

# @chatbot.get('/summarize_texts')
# async def summarize_texts():
#     conn = db_connect2()
#     cursor = conn.cursor()
#     cursor.execute('SELECT text FROM chats')
#     texts = cursor.fetchall()
#     conn.close()
#     print("texts", texts)
#     # 모든 텍스트를 하나의 문자열로 결합
#     combined_text = ' '.join([text[0] for text in texts])
#     print(combined_text)
#     chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2)

#     prompt = PromptTemplate(
#         input_variables=["step"],
#         template="""{step},
#         Based on the above, analyze what this student's interests are.
#         Lastly, please answer in Korean.
#             """
#     )

#     chain = LLMChain(llm=chat, prompt=prompt)
#     result = chain.run(step=combined_text)
#     print("result", result)
#     return result

# 기존의 /send_student 엔드포인트 코드는 그대로 유지




@chatbot.post('/quiz')
async def sendchat_quiz(item: Item):

    print(item)
    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.7)

    prompt = PromptTemplate(
        input_variables=["exam", "json_schema"],
        template="""You are a Korean middle school teacher. You need to create a quiz for subject.
        {exam}
        Answers to all questions are created in Korean.
        Finally, we respond with the following JSON schema:
        
        {json_schema}
        """
    )
    # Please create one o,x quiz about {quiz} in the {subject} subject.
    chain = LLMChain(llm=chat, prompt=prompt)

    quiz = item.quiz
    subject = item.subject

    result = chain.run(exam=f"""Please create one OX quiz about {quiz} in the {subject} subject.
    Please do not add "1." to your "quiz".
    Please correct answers to the quiz.
    And please answer the quiz.""",
                       json_schema="""{
                       "quiz":,
                       "answer":"
                       }""")
    # print(result)
    result_data  = json.loads(result)
    print(result_data)

    return result_data

@chatbot.post('/quiz2')
async def sendchat_quiz(item: Item):
    print(item)
    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5)

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
    1. Please create only one quiz. But leave out the "(O,X)" characters..
    2. Generate the correct answers for the quiz.
    3. That's right, don't do it. If the answer to the quiz is an "O" write an explanation of why it's correct, and if it's an "X" write an commentory of why it's not correct.""",
                       json_schema="""{
                       "quiz": ,
                       "answer": ,
                       "Commentary" :
                       }""")
    print("result::::",result)

    result_data = json.loads(result)
    if '맞습니다. ' in result_data['Commentary']:
        # '맞습니다.'를 빈 문자열로 치환
        modified_commentary = result_data['Commentary'].replace('맞습니다. ', '')

        # result_data 딕셔너리의 'Commentary'를 수정된 내용으로 업데이트
        result_data['Commentary'] = modified_commentary
    print(result_data)

    return result_data

