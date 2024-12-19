from pydantic import BaseModel, Field


class BlogPlannerOutput(BaseModel):
    sections: list[str] = Field(
        ...,
        description="Given a question give a proper breakdown of the question into multiple section headings.",
    )


class BlogContent(BaseModel):
    paragraph: str = Field(
        ...,
        description="A paragraph of text for the given topic heading",
    )


class PromptOutput(BaseModel):
    prompt: str = Field(
        ...,
        description="Given a paragraph from the blog generate a prompt to generare suitable image for the same.",
    )


class TitleTags(BaseModel):
    title: str = Field(
        ...,
        description="A title suitable for the blog",
    )
    tags: list[str] = Field(
        ...,
        description="A list of tags suitable for the blog",
    )
