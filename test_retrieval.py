from app.core.vectorstore import get_collection

def test_query(query_text, n_results=3):
    collection = get_collection()
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
    )

    print(f"\nQuery: {query_text}")
    print("-" * 60)
    for i, (doc_id, distance) in enumerate(zip(results["ids"][0], results["distances"][0])):
        print(f"{i+1}. {doc_id}  (distance: {distance:.4f})")

if __name__ == "__main__":
    test_query("I'm a girl in class 10, family income is 1.5 lakh per year")
    test_query("I'm SC category, got into IIT Bombay, family earns 3 lakh")
    test_query("unemployed OBC, finished my masters degree, looking for research funding")
    test_query("I want to start a small business, I'm a woman")