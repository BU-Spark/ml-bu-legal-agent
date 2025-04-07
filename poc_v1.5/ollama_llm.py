from langchain.llms import Ollama
from llm_interface import LLM
from prompt_templates import FIFTH_GRADE_PROMPT_TEMPLATE

class OllamaLLM(LLM):
    def __init__(self, model_name="deepseek-r1:1.5b"):
        self.llm = Ollama(model=model_name)
        self.prompt_template = FIFTH_GRADE_PROMPT_TEMPLATE + "\nHuman: {question}"

    def generate_response(self, question: str, context: str) -> str:
        prompt = self.prompt_template.format(context=context, question=question)
        try:
            response = self.llm(prompt)
            return response
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return "Sorry, there was an error processing your request with Ollama."