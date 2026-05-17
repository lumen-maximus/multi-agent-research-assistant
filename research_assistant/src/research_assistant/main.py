from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from research_assistant.graph import get_compiled_graph


def main():
    graph = get_compiled_graph()
    thread_id = "main-conversation"
    config = RunnableConfig(configurable={"thread_id": thread_id})

    print("Research Assistant (type 'quit' or 'exit' to stop)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        result = graph.invoke(
            {"messages": [HumanMessage(content=user_input)], "query": user_input},
            config,
        )

        # Check for interrupt
        snapshot = graph.get_state(config)
        while snapshot.next:
            # Graph is interrupted — collect clarification
            interrupt_value = snapshot.tasks[0].interrupts[0].value if snapshot.tasks else None
            if interrupt_value:
                print(f"\nAssistant: {interrupt_value}")
            else:
                print("\nAssistant: Could you clarify your question?")

            try:
                clarification = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return

            if clarification.lower() in ("quit", "exit"):
                print("Goodbye!")
                return

            result = graph.invoke(
                Command(resume=clarification),
                config,
            )
            snapshot = graph.get_state(config)

        response = result.get("response", "")
        if response:
            print(f"\nAssistant: {response}")
        else:
            print("\nAssistant: I wasn't able to generate a response. Please try again.")


if __name__ == "__main__":
    main()
