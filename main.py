import typesense
from typesense.configuration import ConfigDict, NodeConfigDict
from typesense.exceptions import ObjectNotFound
from typesense.types.collection import CollectionCreateSchema

foo_schema: CollectionCreateSchema = {
    "name": "foo",
    "fields": [
        {"name": "description", "type": "string", "token_separators": ["'", ","]}
    ],
}


def main() -> None:
    client = typesense.Client(
        ConfigDict(
            api_key="foo",
            nodes=[NodeConfigDict(host="localhost", port=4242, protocol="http")],
        )
    )
    try:
        client.collections["foo"].delete()
        client.collections["bar"].delete()
    except ObjectNotFound:
        pass

    client.collections.create(foo_schema)
    client.collections["foo"].documents.create(
        {"description": "J'adore la Supply Chain, entre autres choses intéressantes."}
    )

    results = client.collections["foo"].documents.search(
        {"q": "supply cHaIn", "query_by": "description"}
    )

    hits = results["hits"]
    assert len(hits) == 1, "Should hit one document!"

    hit = hits[0]
    highlight = hit["highlight"]
    matched_tokens = highlight["description"]["matched_tokens"]

    assert set(matched_tokens) == {"Supply", "Chain"}, (
        f"Should only match on two tokens, matched {set(matched_tokens)}!"
    )


if __name__ == "__main__":
    main()
