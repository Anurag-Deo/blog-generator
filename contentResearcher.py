from concurrent.futures import ThreadPoolExecutor, as_completed

from dataModels import BlogContent
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate


class ContentResearcher:
    def __init__(self, chat_model, tool):
        self.chat_model = chat_model
        self.tool = tool
        self.parser = JsonOutputParser(pydantic_object=BlogContent)

    def process_query(self, query):
        urls = []
        searches = self.tool.invoke({"query": query})
        for item in searches:
            urls.append(item["url"])

        loader = UnstructuredURLLoader(urls=urls)
        data = loader.load()

        combined_content = " ".join([doc.page_content for doc in data])

        prompt_template = """
You are an expert blog writer. You are given a blog topic and the corresponding supporting documents. Your task is to write a paragraph for the topic based on the information in the documents. The paragraph should be informative and well-structured. Write it long and descriptive. Try to explain your points with examples. The paragraph should be well written in professional tone which is good to be published in any online research based blogging website. You should only return the paragraph generated for the blog without any other statement in the response.
{format_instructions}
The Documents are as follows:
{document}

The topic is:
{question}
"""
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["document", "question"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        chain = prompt | self.chat_model | self.parser

        try:
            response = chain.invoke({"document": combined_content, "question": query})
        except Exception:
            response = {"paragraph": ""}

        return response["paragraph"]

    def research_content(self, sections):
        blog = []
        with ThreadPoolExecutor() as executor:
            future_to_query = {
                executor.submit(self.process_query, query): query
                for query in sections["sections"]
            }
            for future in as_completed(future_to_query):
                try:
                    blog.append(future.result())
                except Exception as e:
                    print(f"Error processing query: {e}")
                    blog.append("")
        return blog
