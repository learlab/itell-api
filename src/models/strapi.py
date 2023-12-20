from typing import Optional
from pydantic import BaseModel, Field, Json
from pydantic import ValidationError

from typing import TypeVar, Generic
from pydantic.generics import GenericModel


class Chunk(BaseModel):
    id: int
    Slug: str
    Header: str
    CleanText: str
    KeyPhrase: Optional[Json[list[str]]]
    QuestionAnswerResponse: Optional[Optional[str]] = None
    Question: Optional[str] = None
    ConstructedResponse: Optional[str] = None


class PageBase(BaseModel):
    Title: str
    slug: str
    HasSummary: bool


class TextBase(BaseModel):
    Title: str
    Owner: str
    Description: Optional[str]
    slug: str


class TextData(BaseModel):
    id: int
    attributes: TextBase


class Text(BaseModel):
    data: TextData


# Page Types


class PageWithChunks(PageBase):
    Content: list[Chunk] = Field(..., min_items=1)


class PageWithMeta(PageBase):
    text: Text


# Fancy Generic Types for Defining Pages Populated with Specific Values

Populus = TypeVar("Populus")


class PopulatedPage(GenericModel, Generic[Populus]):
    id: int
    attributes: Populus


class ChunksByPage(BaseModel):
    data: list[PopulatedPage[PageWithChunks]] = Field(..., min_items=1)


class PageMeta(BaseModel):
    data: list[PopulatedPage[PageWithMeta]] = Field(..., min_items=1)


if __name__ == "__main__":
    test_strings = [
        ("rich_response", ChunksByPage, r"""{"data":[{"id":48,"attributes":{"Title":"Legal and Political Systems of the World","createdAt":"2023-12-04T20:51:10.445Z","updatedAt":"2023-12-16T02:37:14.714Z","publishedAt":"2023-12-04T20:51:16.429Z","slug":"legal-and-political-systems-of-the-world","HasSummary":true,"Content":[{"id":37,"__component":"page.plain-chunk","CleanText":"- Describe how the common-law system differs from the civil-law system.\n\nOther legal and political systems are very different from the US system, which came from English common-law traditions and the framers of the US Constitution. Our legal and political traditions are different both in what kinds of laws we make and honor and in how disputes are resolved in court.","MDX":"<Info title=\"LEARNING OBJECTIVES\">\\- Describe how the common-law system differs from the civil-law system.</Info>\n\nOther legal and political systems are very different from the US system, which came from English common-law traditions and the framers of the US Constitution. Our legal and political traditions are different both in what kinds of laws we make and honor and in how disputes are resolved in court.","Text":"<div class=\"raw-html-embed\"><info title=\"LEARNING OBJECTIVES\">\n- Describe how the common-law system differs from the civil-law system.\n</info></div><p>Other legal and political systems are very different from the US system, which came from English common-law traditions and the framers of the US Constitution. Our legal and political traditions are different both in what kinds of laws we make and honor and in how disputes are resolved in court.</p>","Slug":"Legal-and-Political-Systems-of-the-World-37pt","Header":"Legal and Political Systems of the World"},{"id":173,"__component":"page.chunk","Question":"What is one key difference between common-law systems and civil-law systems?","CleanText":"Comparing Common-Law Systems with Other Legal Systems\n\nThe common-law tradition is unique to England, the United States, and former colonies of the British Empire. Although there are differences among common-law systems (e.g., most nations do not permit their judiciaries to declare legislative acts unconstitutional; some nations use the jury less frequently), all of them recognize the use of precedent in judicial cases, and none of them relies on the comprehensive, legislative codes that are prevalent in civil-law systems.","MDX":"### Comparing Common-Law Systems with Other Legal Systems\n\nThe common-law tradition is unique to England, the United States, and former colonies of the British Empire. Although there are differences among common-law systems (e.g., most nations do not permit their judiciaries to declare legislative acts unconstitutional; some nations use the jury less frequently), all of them recognize the use of precedent in judicial cases, and none of them relies on the comprehensive, legislative codes that are prevalent in civil-law systems.","Text":"<h3><strong>Comparing Common-Law Systems with Other Legal Systems</strong></h3><p>The common-law tradition is unique to England, the United States, and former colonies of the British Empire. Although there are differences among common-law systems (e.g., most nations do not permit their judiciaries to declare legislative acts unconstitutional; some nations use the jury less frequently), all of them recognize the use of precedent in judicial cases, and none of them relies on the comprehensive, legislative codes that are prevalent in civil-law systems.</p>","QuestionAnswerResponse":"{\"question\": \"What is one key difference between common-law systems and civil-law systems?\", \"answer\": \"Common-law systems recognize the use of precedent in judicial cases, while civil-law systems rely on comprehensive legislative codes.\"}","KeyPhrase":"[\"common-law tradition\", \"England\", \"United States\", \"former colonies\", \"precedent in judicial cases\"]","ConstructedResponse":"Common-law systems recognize the use of precedent in judicial cases, while civil-law systems rely on comprehensive legislative codes.","Slug":"Comparing-Common-Law-Systems-with-Other-Legal-Systems-173t","Header":"Comparing Common-Law Systems with Other Legal Systems"},{"id":174,"__component":"page.chunk","Question":"What are some legal systems that differ significantly from common-law and civil-law systems?","CleanText":"Civil-Law Systems\n\nThe main alternative to the common-law legal system was developed in Europe and is based in Roman and Napoleonic law. A civil-law or code-law system is one where all the legal rules are in one or more comprehensive legislative enactments. During Napoleon’s reign, a comprehensive book of laws—a code—was developed for all of France. The code covered criminal law, criminal procedure, noncriminal law and procedure, and commercial law. The rules of the code are still used today in France and in other continental European legal systems. The code is used to resolve particular cases, usually by judges without a jury. Moreover, the judges are not required to follow the decisions of other courts in similar cases. As George Cameron of the University of Michigan has noted, “The law is in the code, not in the cases.” He goes on to note, “Where several cases all have interpreted a provision in a particular way, the French courts may feel bound to reach the same result in future cases, under the doctrine of jurisprudence constante. The major agency for growth and change, however, is the legislature, not the courts.”\n\nCivil-law systems are used throughout Europe as well as in Central and South America. Some nations in Asia and Africa have also adopted codes based on European civil law. Germany, Holland, Spain, France, and Portugal all had colonies outside of Europe, and many of these colonies adopted the legal practices that were imposed on them by colonial rule, much like the original thirteen states of the United States, which adopted English common-law practices.\n\nOne source of possible confusion at this point is that we have already referred to US civil law in contrast to criminal law. But the European civil law covers both civil and criminal law.\n\nThere are also legal systems that differ significantly from the common-law and civil-law systems. The communist and socialist legal systems that remain (e.g., in Cuba and North Korea) operate on very different assumptions than those of either English common law or European civil law. Islamic and other religion-based systems of law bring different values and assumptions to social and commercial relations.","MDX":"### Civil-Law Systems\n\nThe main alternative to the common-law legal system was developed in Europe and is based in Roman and Napoleonic law. A civil-law or code-law system is one where all the legal rules are in one or more comprehensive legislative enactments. During Napoleon’s reign, a comprehensive book of laws—a code—was developed for all of France. The code covered criminal law, criminal procedure, noncriminal law and procedure, and commercial law. The rules of the code are still used today in France and in other continental European legal systems. The code is used to resolve particular cases, usually by judges without a jury. Moreover, the judges are not required to follow the decisions of other courts in similar cases. As George Cameron of the University of Michigan has noted, “The law is in the code, not in the cases.” He goes on to note, “Where several cases all have interpreted a provision in a particular way, the French courts may feel bound to reach the same result in future cases, under the doctrine of __jurisprudence constante.__ The major agency for growth and change, however, is the legislature, not the courts.”\n\nCivil-law systems are used throughout Europe as well as in Central and South America. Some nations in Asia and Africa have also adopted codes based on European civil law. Germany, Holland, Spain, France, and Portugal all had colonies outside of Europe, and many of these colonies adopted the legal practices that were imposed on them by colonial rule, much like the original thirteen states of the United States, which adopted English common-law practices.\n\nOne source of possible confusion at this point is that we have already referred to US civil law in contrast to criminal law. But the European civil law covers both civil and criminal law.\n\nThere are also legal systems that differ significantly from the common-law and civil-law systems. The communist and socialist legal systems that remain (e.g., in Cuba and North Korea) operate on very different assumptions than those of either English common law or European civil law. Islamic and other religion-based systems of law bring different values and assumptions to social and commercial relations.","Text":"<h3><strong>Civil-Law Systems</strong></h3><p class=\"para editable block\" id=\"mayer_1.0-ch01_s05_s02_p01\">The main alternative to the common-law legal system was developed in Europe and is based in Roman and Napoleonic law. A civil-law or code-law system is one where all the legal rules are in one or more comprehensive legislative enactments. During Napoleon’s reign, a comprehensive book of laws—a code—was developed for all of France. The code covered criminal law, criminal procedure, noncriminal law and procedure, and commercial law. The rules of the code are still used today in France and in other continental European legal systems. The code is used to resolve particular cases, usually by judges without a jury. Moreover, the judges are not required to follow the decisions of other courts in similar cases. As George Cameron of the University of Michigan has noted, “The law is in the code, not in the cases.” He goes on to note, “Where several cases all have interpreted a provision in a particular way, the French courts may feel bound to reach the same result in future cases, under the doctrine of <em class=\"emphasis\"><i>jurisprudence constante.</i></em> The major agency for growth and change, however, is the legislature, not the courts.”</p><p class=\"para editable block\" id=\"mayer_1.0-ch01_s05_s02_p02\">Civil-law systems are used throughout Europe as well as in Central and South America. Some nations in Asia and Africa have also adopted codes based on European civil law. Germany, Holland, Spain, France, and Portugal all had colonies outside of Europe, and many of these colonies adopted the legal practices that were imposed on them by colonial rule, much like the original thirteen states of the United States, which adopted English common-law practices.</p><p class=\"para editable block\" id=\"mayer_1.0-ch01_s05_s02_p03\">One source of possible confusion at this point is that we have already referred to US civil law in contrast to criminal law. But the European civil law covers both civil and criminal law.</p><p class=\"para editable block\" id=\"mayer_1.0-ch01_s05_s02_p04\">There are also legal systems that differ significantly from the common-law and civil-law systems. The communist and socialist legal systems that remain (e.g., in Cuba and North Korea) operate on very different assumptions than those of either English common law or European civil law. Islamic and other religion-based systems of law bring different values and assumptions to social and commercial relations.</p>","QuestionAnswerResponse":"{\"question\": \"What are some legal systems that differ significantly from common-law and civil-law systems?\", \"answer\": \"Communist, socialist, and religion-based systems of law.\"}","KeyPhrase":"[\"common-law legal system\", \"civil-law or code-law system\", \"comprehensive legislative enactments\", \"continental European legal systems\", \"European civil law\"]","ConstructedResponse":"Communist, socialist, and religion-based systems of law.","Slug":"Civil-Law-Systems-174t","Header":"Civil-Law Systems"}]}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}"""),  # noqa: E501
        ("no_page", ChunksByPage, r"""{"data":[],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":0,"total":0}}}"""),  # noqa: E501
        ("no_chunks", ChunksByPage, r"""{"data":[{"id":48,"attributes":{"Title":"Legal and Political Systems of the World","createdAt":"2023-12-04T20:51:10.445Z","updatedAt":"2023-12-16T02:37:14.714Z","publishedAt":"2023-12-04T20:51:16.429Z","slug":"legal-and-political-systems-of-the-world","HasSummary":true,"Content":[]}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}"""),  # noqa: E501
        ("title_response", PageMeta, r"""{"data":[{"id":8,"attributes":{"Title":"What Is Law?","createdAt":"2023-11-30T03:25:35.670Z","updatedAt":"2023-12-16T07:19:33.823Z","publishedAt":"2023-11-30T03:25:51.771Z","slug":"what-is-law","HasSummary":true,"text":{"data":{"id":3,"attributes":{"Title":"Business Law and the Legal Environment","Owner":"LEAR Lab","Description":null,"createdAt":"2023-11-29T08:23:17.220Z","updatedAt":"2023-11-30T01:19:23.148Z","publishedAt":"2023-11-29T08:23:27.555Z","slug":"business-law-and-the-legal-environment"}}}}}],"meta":{"pagination":{"page":1,"pageSize":25,"pageCount":1,"total":1}}}""")  # noqa: E501
    ]
    for key, model, test_str in test_strings:
        try:
            m = model.parse_raw(test_str)
            # print(m.data[0].attributes.Content[1].KeyPhrase)
        except ValidationError as error:
            print(f"{key:-^40}")
            print(error)
