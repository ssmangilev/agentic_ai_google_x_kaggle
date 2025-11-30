import os

from google.adk_community.memory import OpenMemoryService


memory_service_url = os.getenv('OPENMEMORY_SERVICE_URL')
memory_service_api_key = os.getenv('OPENMEMORY_SERVICE_API_KEY')

if not memory_service_url or not memory_service_api_key:
    raise Exception('Memory service credentials were not provided')

memory_service = OpenMemoryService(
    base_url=memory_service_url,
    api_key=memory_service_api_key
)
