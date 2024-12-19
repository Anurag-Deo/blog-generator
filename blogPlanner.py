from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dataModels import BlogPlannerOutput

class BlogPlanner:
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.parser = JsonOutputParser(pydantic_object=BlogPlannerOutput)
        self.prompt = PromptTemplate(
            template="""You are an expert blog writer. You are given a blog topic you need to structure the blog into several sections. Break down the blog into related sub-sections. It's a great idea to structure it into 7-10 sections don't go beyond that. For example, if the topic is about transformers, then you might have sections like History of transformers, Types of transformers, Applications of transformers, etc. Your goal is to generate a list of sections that will help you structure the blog.
{format_instructions}
The topic is: {query}
""",
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.chain = self.prompt | self.chat_model | self.parser

    def plan_sections(self, topic):
        return self.chain.invoke({"query": topic})
