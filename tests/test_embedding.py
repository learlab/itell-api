import pytest
import os


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_generate_embeddings(client):
    response = await client.post(
        "/generate/embedding",
        json={
            "text_slug": "test_text",
            "module_slug": "test_module",
            "chapter_slug": "test_chapter",
            "page_slug": "test_page",
            "chunk_slug": "test_chunk_1",
            "content": """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum. Sed nec felis pellentesque, faucibus libero vel, dictum justo. Aliquam erat volutpat. Ut et libero magna. Fusce nec turpis vel leo malesuada tincidunt. Nullam non dui vitae diam sollicitudin ullamcorper. Sed ac elit non mi pharetra dictum. Praesent tincidunt, orci ac commodo consequat, augue mauris gravida turpis.""",
        },
    )
    assert response.status_code == 201

    response = await client.post(
        "/generate/embedding",
        json={
            "text_slug": "test_text",
            "module_slug": "test_module",
            "chapter_slug": "test_chapter",
            "page_slug": "test_page",
            "chunk_slug": "test_chunk_2",
            "content": """In interdum ullamcorper dolor et vulputate. Nulla facilisi. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante. Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. Mauris placerat eleifend leo. Quisque sit amet est et sapien ullamcorper pharetra.""",
        },
    )
    assert response.status_code == 201

    response = await client.post(
        "/generate/embedding",
        json={
            "text_slug": "test_text",
            "module_slug": "test_module",
            "chapter_slug": "test_chapter",
            "page_slug": "test_page",
            "chunk_slug": "test_chunk_3",
            "content": """Vestibulum erat wisi, condimentum sed, commodo vitae, ornare sit amet, wisi. Aenean fermentum, elit eget tincidunt condimentum, eros ipsum rutrum orci, sagittis tempus lacus enim ac dui. Donec non enim in turpis pulvinar facilisis. Ut felis. Praesent dapibus, neque id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros eu erat. Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan porttitor, facilisis luctus, metus.""",
        },
    )
    assert response.status_code == 201


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_retrieve_chunks(client):
    response = await client.post(
        "/retrieve/chunks",
        json={
            "text_slug": "test_text",
            "page_slug": "test_page",
            "text": "Vestibulum erat wisi, condimentum sed, commodo vitae, ornare sit amet, wisi. Aenean fermentum, elit eget tincidunt condimentum, eros ipsum rutrum orci, sagittis tempus lacus enim ac dui. Donec non enim in turpis pulvinar facilisis. Ut felis. Praesent dapibus, neque id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros eu erat. Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan porttitor, facilisis luctus, metus.",
        },
    )
    assert response.status_code == 200
