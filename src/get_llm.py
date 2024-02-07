# from dotenv import load_dotenv
# load_dotenv()

from langchain.schema import SystemMessage, HumanMessage

from llm_commons.proxy.base import set_proxy_version
from llm_commons.proxy.identity import AICoreProxyClient
from llm_commons.langchain.proxy import init_llm

import settings

AICORE_LLM_CLIENT_ID = settings.AICORE_LLM_CLIENT_ID
AICORE_LLM_CLIENT_SECRET = settings.AICORE_LLM_CLIENT_SECRET
AICORE_LLM_AUTH_URL = settings.AICORE_LLM_AUTH_URL
AICORE_LLM_API_BASE = settings.AICORE_LLM_API_BASE
AICORE_LLM_RESOURCE_GROUP = settings.AICORE_LLM_RESOURCE_GROUP

# import logging

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

def get_llm(prompt):
    set_proxy_version('aicore') # for \an AI Core proxy
    proxy_client = AICoreProxyClient()
    proxy_client.get_deployments() # to cache the deployment data

    llm = init_llm(model_name="gpt-35-turbo-16k", 
                proxy_client=proxy_client,
                temperature=0
                    )

    messages = [
        SystemMessage(
            content="You are a helpful assistant that generates contents of powerpoint."
        ),
        HumanMessage(
            content=prompt
        ),
    ]
    
    explanation = llm(messages)
    return explanation.content