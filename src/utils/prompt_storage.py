from abc import ABC, abstractmethod

from langfuse import get_client

from dotenv import load_dotenv

# 1. Load the environment variables here, before any other imports
# that might rely on them (like database connectors or Langfuse clients).
load_dotenv()


langfuse = get_client()


class PromptStorageABC(ABC):

    @property
    def client():
        pass

    def get_prompt(self, name: str) -> str:
        pass

    @property
    def is_authenticated(self) -> bool:
        pass


class BasePromptStorage(PromptStorageABC):

    def __init__(self, *args, **kwargs):
        self._client_instance = kwargs['client']

    @property
    def client(self):
        return self._client_instance


class LangfusePromptStorage(BasePromptStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def is_authenticated(self):
        return self.client.auth_check()

    def get_prompt(self, name: str) -> str:
        try:
            prompt = self.client.get_prompt(name=name).compile()
            return prompt
        except Exception:
            raise Exception('Prompt name was not found!')


langfuse_prompt_storage = LangfusePromptStorage(client=langfuse)
