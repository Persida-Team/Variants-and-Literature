import os
from dotenv import load_dotenv

load_dotenv()

def get_env_or_fail(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value