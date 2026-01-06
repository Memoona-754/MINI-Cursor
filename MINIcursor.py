from google import genai
from google.genai import types
import os

client = genai.Client(api_key=API_KEY)


def read_file(path: str) -> str:
    """Read file contents"""
    with open(path) as f:
        return f.read()


def list_files(path: str = ".") -> str:
    """List files in directory"""
    return "\n".join(os.listdir(path or "."))


def edit_file(path: str, old_str: str, new_str: str) -> str:
    """Create or edit a file"""
    if old_str == "":  # Create new file
        with open(path, "w") as f:
            f.write(new_str)
        return f"Created {path}"

    content = read_file(path)
    with open(path, "w") as f:
        f.write(content.replace(old_str, new_str))
    return "OK"


# ===== STEP 2: Map tools for execution =====
tools = [read_file, list_files, edit_file]
tool_map = {fn.__name__: fn for fn in tools}


# ===== STEP 3: System prompt =====
SYSTEM = """You are a coding assistant. Use your tools to help users:
- edit_file with old_str="" creates new files
- read_file reads file contents
- list_files shows directory contents
Always use tools instead of just showing code."""


# ===== STEP 4: The agent loop =====
def run_agent():
    chat = client.chats.create(
        model="gemini-3-pro-preview",
        config={"tools": tools, "system_instruction": SYSTEM}
    )

    while True:
        user_input = input("You: ")
        response = chat.send_message(user_input)

        # Process response until no more tool calls
        while True:
            tool_called = False

            for part in response.candidates[0].content.parts:
                if part.text:
                    print(f"Agent: {part.text}")

                if part.function_call:
                    tool_called = True
                    fn = part.function_call

                    # Run the tool
                    result = tool_map[fn.name](**fn.args)

                    # Send result back to model
                    response = chat.send_message(
                        types.Part.from_function_response(name=fn.name, response={"result": result})
                    )
                    break

            if not tool_called:
                break


if __name__ == "__main__":
    run_agent()

Comment
