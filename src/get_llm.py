import settings

from llm_commons.proxy.base import set_proxy_version
from llm_commons.proxy.identity import AICoreProxyClient
from llm_commons.langchain.proxy import init_llm, init_embedding_model


AICORE_LLM_CLIENT_ID = settings.AICORE_LLM_CLIENT_ID
AICORE_LLM_CLIENT_SECRET = settings.AICORE_LLM_CLIENT_SECRET
AICORE_LLM_AUTH_URL = settings.AICORE_LLM_AUTH_URL
AICORE_LLM_API_BASE = settings.AICORE_LLM_API_BASE
AICORE_LLM_RESOURCE_GROUP = settings.AICORE_LLM_RESOURCE_GROUP


def get_llm():
    set_proxy_version('aicore') # for an AI Core proxy
    proxy_client = AICoreProxyClient()
    proxy_client.get_deployments() # to cache the deployment data
    LANGUAGE_MODEL = "gpt-35-turbo-16k"
    # LANGUAGE_MODEL = "gpt-4"

    llm = init_llm(model_name=LANGUAGE_MODEL, 
            proxy_client=proxy_client,
            temperature=0.3,
            max_tokens=1000
            )

    return llm

def get_embed():
    set_proxy_version('aicore') # for an AI Core proxy
    proxy_client = AICoreProxyClient()
    proxy_client.get_deployments() # to cache the deployment data

    embed = init_embedding_model(model_name="text-embedding-ada-002")
    return embed