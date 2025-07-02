from dotenv import load_dotenv
from typing import Literal, Optional ,Any
from pydantic import BaseModel, Field
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Load environment variables
load_dotenv()

class ConfigLoader:
    def __init__(self):
        print(f"Loaded config.....")
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]


class ModelLoader(BaseModel): 
    model_provider: Literal["groq", "google"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        self.config = ConfigLoader()

    class Config:
        arbitrary_types_allowed = True 

    def load_llm(self):
        """Load the LLM based on the provider and model name."""
        print("Loading LLM...")
        print(f"Loading model from provider: {self.model_provider}")
        
        if not self.config:
            self.config = ConfigLoader()

        if self.model_provider == "groq":
            print("Loading LLM from Groq..............")
            groq_api_key = os.getenv("GROQ_API_KEY")
            model_name = self.config["llm"]["groq"]["model_name"]
            llm = ChatGroq(model=model_name, api_key=groq_api_key)

        elif self.model_provider == "google":
            print("Loading LLM from Google..............")
            google_api_key = os.getenv("GOOGLE_API_KEY")
            model_name = self.config["llm"]["google"]["model_name"]
            llm = ChatGoogleGenerativeAI(model=model_name, api_key=google_api_key)

        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

        return llm
