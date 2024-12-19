import os
import requests
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dataModels import TitleTags

class BlogPublisher:
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.parser = JsonOutputParser(pydantic_object=TitleTags)

    def generate_title_tags(self, text_blog):
        prompt = PromptTemplate(
            template="""You are an expert blog writer. You are provided with a blog and you need to generate a suitable title and a list of tags for the blog. Make sure you don't append any other thing in the start or end of the title just return the title.
{format_instructions}
The paragraph is:
{query}
""",
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        chain = prompt | self.chat_model | self.parser
        response = chain.invoke({"query": text_blog})
        return response["title"], response["tags"]

    def save_blog(self, title, text_blog):
        with open(f"{title}.md", "w") as file:
            file.write(text_blog)

    def post_to_devto(self, title, text_blog, hosted_urls, sections, tags):
        url = "https://dev.to/api/articles"
        headers = {
            "Content-Type": "application/json",
            "api-key": os.environ["DEVTO_API_KEY"],
        }
        payload = {
            "article": {
                "title": title,
                "body_markdown": text_blog,
                "published": False,
                "series": "Artificial Intelligence",
                "main_image": hosted_urls[0],
                "canonical_url": hosted_urls[0],
                "description": f"The article discusses about {', '.join(sections['sections'])}",
                "tags": ", ".join(tags),
                "organization_id": 0,
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                print("Article successfully created:", response.json())
            else:
                print("Failed to create article:", response.status_code, response.text)

        except Exception as e:
            print("An error occurred:", str(e))
