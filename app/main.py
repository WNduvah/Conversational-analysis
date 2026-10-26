from .graph import build_graph

def main():
    graph = build_graph()
    print("Conversational Analytics Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        try:
            result = graph.invoke({"question": question, "retries": 0})
            print(f"\nAssistant: {result['answer']}\n")
        except Exception as exc:
            print(f"\nAssistant: Application error: {exc}\n")

if __name__ == "__main__":
    main()
