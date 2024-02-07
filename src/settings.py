import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

AICORE_LLM_CLIENT_ID = os.environ.get("AICORE_LLM_CLIENT_ID")
AICORE_LLM_CLIENT_SECRET = os.environ.get("AICORE_LLM_CLIENT_SECRET")
AICORE_LLM_AUTH_URL = os.environ.get("AICORE_LLM_AUTH_URL")
AICORE_LLM_API_BASE = os.environ.get("AICORE_LLM_API_BASE")
AICORE_LLM_RESOURCE_GROUP = os.environ.get("AICORE_LLM_RESOURCE_GROUP")