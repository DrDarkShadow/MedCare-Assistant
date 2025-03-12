import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Azure LLM Initialization
llm = AzureChatOpenAI(
    azure_endpoint="https://project-komp.openai.azure.com/",
    azure_deployment="gpt-4o",
    api_version="2023-09-01-preview",
    api_key="CdTiGBHZd04q2kNbXKzMud27LvssSsfm0RkrTDlvPpDdHLKOknK9JQQJ99BAACYeBjFXJ3w3AAABACOGvVoL",
    temperature=0
)


def get_ai_response(user_input):
    response = llm.invoke(user_input)
    return response.content
