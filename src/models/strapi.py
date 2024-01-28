from typing import Optional
from pydantic import BaseModel, Field, Json
from pydantic import ValidationError

from typing import TypeVar, Generic
from pydantic.generics import GenericModel


class Chunk(BaseModel):
    Slug: str
    id: int
    Header: str
    CleanText: str
    KeyPhrase: Optional[Json[list[str]]]
    QuestionAnswerResponse: Optional[Optional[str]] = None
    Question: Optional[str] = None
    ConstructedResponse: Optional[str] = None


class Page(BaseModel):
    slug: str
    Title: str
    HasSummary: bool


class Text(BaseModel):
    slug: str
    Title: str
    Owner: str
    Description: Optional[str]


# Page Types


class Content(Page):
    Content: list[Chunk] = Field(..., min_items=1)


# Fancy Generic Types for Defining Pages Populated with Specific Values

Populus = TypeVar("Populus")


class Response(GenericModel, Generic[Populus]):
    data: Populus


class PopulatedItem(GenericModel, Generic[Populus]):
    id: int
    attributes: Populus


# Constructed Types


class _PageWithText(Page):
    text: Response[PopulatedItem[Text]]


class PageWithText(BaseModel):
    data: list[PopulatedItem[_PageWithText]] = Field(..., min_items=1)


class PageWithChunks(BaseModel):
    data: list[PopulatedItem[Content]] = Field(..., min_items=1)


if __name__ == "__main__":
    from rich import print

    test_strings = [
        (
            "rich_response",
            PageWithChunks,
            r"""{"data":[{"id":48,"attributes":{"Title":"Legal and Political Systems of the World","createdAt":"2023-12-04T20:51:10.445Z","updatedAt":"2023-12-16T02:37:14.714Z","publishedAt":"2023-12-04T20:51:16.429Z","slug":"legal-and-political-systems-of-the-world","HasSummary":true,"Content":[{"id":173,"__component":"page.chunk","Question":"What is one key difference between common-law systems and civil-law systems?","CleanText":"Comparing Common-Law Systems with Other Legal Systems\n\nThe common-law tradition is unique to England, the United States, and former colonies of the British Empire. Although there are differences among common-law systems (e.g., most nations do not permit their judiciaries to declare legislative acts unconstitutional; some nations use the jury less frequently), all of them recognize the use of precedent in judicial cases, and none of them relies on the comprehensive, legislative codes that are prevalent in civil-law systems.","MDX":"### Comparing Common-Law Systems with Other Legal Systems\n\nThe common-law tradition is unique to England, the United States, and former colonies of the British Empire. Although there are differences among common-law systems (e.g., most nations do not permit their judiciaries to declare legislative acts unconstitutional; some nations use the jury less frequently), all of them recognize the use of precedent in judicial cases, and none of them relies on the comprehensive, legislative codes that are prevalent in civil-law systems.","Text":"<h3><strong>Comparing Common-Law Systems with Other Legal Systems</strong></h3><p>The common-law tradition is unique to England, the United States, and former colonies of the British Empire. Although there are differences among common-law systems (e.g., most nations do not permit their judiciaries to declare legislative acts unconstitutional; some nations use the jury less frequently), all of them recognize the use of precedent in judicial cases, and none of them relies on the comprehensive, legislative codes that are prevalent in civil-law systems.</p>","QuestionAnswerResponse":"{\"question\": \"What is one key difference between common-law systems and civil-law systems?\", \"answer\": \"Common-law systems recognize the use of precedent in judicial cases, while civil-law systems rely on comprehensive legislative codes.\"}","KeyPhrase":"[\"common-law tradition\", \"England\", \"United States\", \"former colonies\", \"precedent in judicial cases\"]","ConstructedResponse":"Common-law systems recognize the use of precedent in judicial cases, while civil-law systems rely on comprehensive legislative codes.","Slug":"Comparing-Common-Law-Systems-with-Other-Legal-Systems-173t","Header":"Comparing Common-Law Systems with Other Legal Systems"}]}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}""",  # noqa: E501
        ),
        (
            "no_page",
            PageWithChunks,
            r"""{"data":[],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":0,"total":0}}}""",  # noqa: E501
        ),
        (
            "no_chunks",
            PageWithChunks,
            r"""{"data":[{"id":48,"attributes":{"Title":"Legal and Political Systems of the World","createdAt":"2023-12-04T20:51:10.445Z","updatedAt":"2023-12-16T02:37:14.714Z","publishedAt":"2023-12-04T20:51:16.429Z","slug":"legal-and-political-systems-of-the-world","HasSummary":true,"Content":[]}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}""",  # noqa: E501
        ),
        (
            "title_response",
            PageWithText,
            r"""{"data":[{"id":8,"attributes":{"Title":"What Is Law?","createdAt":"2023-11-30T03:25:35.670Z","updatedAt":"2023-12-16T07:19:33.823Z","publishedAt":"2023-11-30T03:25:51.771Z","slug":"what-is-law","HasSummary":true,"text":{"data":{"id":3,"attributes":{"Title":"Business Law and the Legal Environment","Owner":"LEAR Lab","Description":null,"createdAt":"2023-11-29T08:23:17.220Z","updatedAt":"2023-11-30T01:19:23.148Z","publishedAt":"2023-11-29T08:23:27.555Z","slug":"business-law-and-the-legal-environment"}}}}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}""",  # noqa: E501
        ),
        (
            "empty_text_item",
            PageWithText,
            r"""{"data":[{"id":8,"attributes":{"Title":"What Is Law?","createdAt":"2023-11-30T03:25:35.670Z","updatedAt":"2023-12-16T07:19:33.823Z","publishedAt":"2023-11-30T03:25:51.771Z","slug":"what-is-law","HasSummary":true,"text":{"data":{"id":3,"attributes":{}}}}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}""",  # noqa: E501
        ),
    ]
    for key, model, test_str in test_strings:
        print(f"{key:-^40}")
        try:
            m = model.parse_raw(test_str)
            print(m)
        except ValidationError as error:
            print(error)
