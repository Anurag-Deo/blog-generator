import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatDeepInfra
from langchain_community.tools import TavilySearchResults
from blogPlanner import BlogPlanner
from contentResearcher import ContentResearcher
from imagePromptGenerator import ImagePromptGenerator
from imageGenerator import ImageGenerator
from blogPublisher import BlogPublisher

load_dotenv()
os.environ["DEEPINFRA_API_KEY"] = os.getenv("DEEPINFRA_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["DEVTO_API_KEY"] = os.getenv("DEVTO_API_KEY")

IMG_GEN_MODEL = "black-forest-labs/FLUX-1-schnell"
TOPIC = "Natural Language Processing"


def main():
    chat_model = ChatDeepInfra(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct",
    )
    tool = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=False,
    )

    # Plan the blog sections
    blog_planner = BlogPlanner(chat_model)
    sections = blog_planner.plan_sections(TOPIC)

    # Research content for each section
    content_researcher = ContentResearcher(chat_model, tool)
    blog = content_researcher.research_content(sections)

    # Generate image prompts
    image_prompt_generator = ImagePromptGenerator(chat_model)
    prompts = image_prompt_generator.generate_prompts(blog)

    # Generate images
    image_generator = ImageGenerator(IMG_GEN_MODEL)
    img_links = image_generator.generate_images(prompts)
    saved_image_paths = image_generator.save_images(img_links)
    hosted_urls = image_generator.upload_images(saved_image_paths)

    # Compile the blog content
    text_blog = ""
    for section, content, image_url in zip(sections["sections"], blog, hosted_urls):
        text_blog += f"### **{section}**\n\n{content}\n\n![{section}]({image_url})\n\n"

    # Generate title and tags
    blog_publisher = BlogPublisher(chat_model)
    title, tags = blog_publisher.generate_title_tags(text_blog)

    # Save and publish the blog
    blog_publisher.save_blog(title, text_blog)
    blog_publisher.post_to_devto(title, text_blog, hosted_urls, sections, tags)


if __name__ == "__main__":
    main()
