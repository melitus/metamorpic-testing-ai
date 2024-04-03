import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class CEConfig:
    openai_api = os.getenv("OPENAI_API")
    tmp_dir = os.getenv("TEMP_DIR")
    openai_model_ver = os.getenv("OPENAI_VER")