# Model Agent Harness Architecture

A modular, stateful AI Agent built on Windows using **DeepSeek LLM**, **LangGraph**, and **LangChain**. 

The system implements the **ReAct (Reasoning + Acting)** paradigm, allowing the LLM to autonomously evaluate user intents, invoke local Python tools (e.g., deterministic calculations, file I/O), inspect execution feedback, and maintain persistent multi-turn conversation memory.

---

## Architecture & Tech Stack

* **Language Model**: DeepSeek (`deepseek-chat` / V3 & R1 compatible via OpenAI SDK)
* **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (Stateful graph engine & memory management)
* **Interface Standard**: `langchain-openai` (OpenAI API-compatible adapter)
* **Data Validation**: `pydantic` (JSON Schema tool definitions)
* **Memory**: `MemorySaver` (In-memory thread checkpointer for stateful context tracking)

---

## Getting Started

### 1. Prerequisites
* Python 3.10+ (Tested on Python 3.14)
* A DeepSeek API Key ([Platform Portal](https://platform.deepseek.com/))

### 2. Environment Setup

Clone the repository and isolate the Python environment:

```cmd
# Create virtual environment
python -m venv venv

# Activate on Windows (CMD)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key

Set the DEEPSEEK_API_KEY environment variable in your terminal before running the application:

Windows (CMD):
```cmd
set DEEPSEEK_API_KEY=sk-your-deepseek-api-key
```

Windows (PowerShell):
```
$env:DEEPSEEK_API_KEY="sk-your-deepseek-api-key"
```

Linux / macOS:
```bash
export DEEPSEEK_API_KEY="sk-your-deepseek-api-key"
```

## Usage

Run the agent via the terminal:

```
python main.py
```

Example Prompt
Your Instruction: Calculate (128 + 256) * 3 and save the result along with the calculation steps into a file named output.txt.

Agent Thought-Execution Output

```
Agent is reasoning and dispatching tools...

[Reasoning] Selected Tool: calculate | Args: {'expression': '(128 + 256) * 3'}
[Tool Output] calculate: Result is 1152

[Reasoning] Selected Tool: write_file | Args: {'filename': 'output.txt', 'content': 'Calculation: (128 + 256) * 3 = 1152'}
[Tool Output] write_file: Successfully wrote content to output.txt

Agent Response:
The expression (128 + 256) * 3 evaluates to 1152. I have saved the calculation details to output.txt.
```

## Built-in Tools

### 1. `calculate`
Evaluates mathematical expressions safely using Python's AST parser or custom evaluation logic.

* **Input Parameters**:
  * `expression` (`str`): The math string to evaluate.
* **Return Type**: `str`
* **Example Payload**:
  ```json
  {
    "expression": "(128 + 256) * 3"
  }

### 2. `write_file`
Writes string content to a specified local file using UTF-8 encoding. Automatically creates the file if it does not exist or overwrites it if it already exists.

* **Input Parameters**:
  * `filename` (`str`): Target file name or path.
  * `content` (`str`): Text content to write into the file.
* **Return Type**: `str` (Execution status message)
* **Example Tool Call Payload**:
  ```json
  {
    "filename": "summary.txt",
    "content": "DeepSeek Agent Execution Summary: All operations completed successfully."
  }

## Built-in File Operations

### 3. `read_file`
Reads and returns the complete text content of a target local file using UTF-8 encoding.

* **Input Parameters**:
  * `filename` (`str`): Target file name or relative path to read.
* **Return Type**: `str` (Full file text content or formatted error message if file is not found)
* **Example Tool Call Payload**:
  ```json
  {
    "filename": "output.txt"
  }

## Security & Best Practices

Environment Safety: API keys are passed strictly through system environment variables and are never hardcoded.

Ignored Files: .gitignore is configured to exclude venv/, environment variables (.env), log files, and local .txt outputs generated during runtime testing.
