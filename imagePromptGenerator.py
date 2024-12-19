from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dataModels import PromptOutput


class ImagePromptGenerator:
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.parser = JsonOutputParser(pydantic_object=PromptOutput)

    def generate_prompt(self, paragraph):
        prompt_template = """
You are an expert prompt writer. You are given a paragraph and you need to write a prompt to generate a suitable image that should accompany the paragraph. You don't need to generate the image, you just need to give a detailed prompt that I can use with models like DALL-E to generate an image. The prompt should contain all the necessary information related so that it can be easily generated. Give the response in the form of a paragraph without any other text added at the start or at the end.
{format_instructions}
The paragraph is:
{query}
"""
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        chain = prompt | self.chat_model | self.parser

        try:
            response = chain.invoke({"query": paragraph})
        except Exception:
            response = {"prompt": ""}

        return response["prompt"]

    def generate_prompts(self, blog):
        prompts = []
        with ThreadPoolExecutor() as executor:
            future_to_paragraph = {
                executor.submit(self.generate_prompt, paragraph): paragraph
                for paragraph in blog
            }
            for future in as_completed(future_to_paragraph):
                try:
                    prompts.append(future.result())
                except Exception as e:
                    print(f"Error generating prompt: {e}")
                    prompts.append("")
        return prompts
