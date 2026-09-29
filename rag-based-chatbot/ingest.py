from app.indexer import index_documents


if __name__ == "__main__":
    result = index_documents()
    print(
        "Index ready: "
        f"{result['documents']} documents, {result['pages']} pages, "
        f"{result['chunks']} chunks."
    )
