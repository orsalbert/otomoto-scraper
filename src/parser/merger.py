def merge_jsonld_and_graphql(jsonld, graphql):
    merged = []

    for gql_item in graphql:
        match = next(
            (
                ld
                for ld in jsonld
                if ld["price"] == gql_item["price"]
                and ld["mileage"] == gql_item["mileage"]
            ),
            {},
        )

        merged.append({**match, **gql_item})

    return merged


if __name__ == "__main__":

    from json_ld_parser import parse_json_ld
    from graphql_parser import parse_graphql
    import os

    html_file_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/html_snapshots/volkswagen_taigo_page_1.html",
    ).replace("\\", "/")

    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    jsonld = parse_json_ld(html_content)
    graphql = parse_graphql(html_content)

    merged = merge_jsonld_and_graphql(jsonld, graphql)
    for item in jsonld:
        print(item)
