from langchain_core.tools import Tool


thinking_tool = Tool(
    name="thinking_logger",
    description="Logs the LLM's current reasoning step",
    func=lambda msg: print(f"[THINK] {msg}")
)