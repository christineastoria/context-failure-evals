# Context Management with LangSmith Evaluations

> ⚠️ **Work in Progress**: This demo is being refined to show clear metrics demonstrating the impact of context management strategies.


## Context Management Patterns
Context engineering is controlling what makes it into your prompt, and managing context incorrectly can lead to bugs and unexpected behaviors. The aim of this notebook is to demonstrate four common context management pitfalls, and how to use LangSmith to evaluate, iterate, and develop better strategies for context management to build more reliable agents. 
<img width="857" height="386" alt="Screenshot 2025-12-20 at 8 27 22 AM" src="https://github.com/user-attachments/assets/dab73fd5-bb04-4257-972f-cc7c31e663b1" />



### 1. Context Confusion

Demonstrating how **context confusion** - superfluous context from excessive tools, verbose instructions, and irrelevant information - degrades LLM agent performance, and how to fix it with LangSmith evaluations.

## The Problem

Adding more tools to an agent seems helpful, but the Berkeley Function-Calling Leaderboard shows **every model performs worse with more tools**. This is context confusion: too much in the context leads to poor tool selection, unnecessary calls, and incorrect responses.

Three problems measured with **trajectory-based evaluation**:

1. **Tool Overload** - ~75 tools → confusion and poor selection
2. **Irrelevant Noise** - Unrelated tools distract even at moderate counts  
3. **Instruction Bloat** - Verbose multi-domain instructions reduce focus

## Evaluators in LangSmith

- **Trajectory Match**: Do tool calls match expected tools?
- **Correctness** (openevals): Is the response accurate?
- **LLM Trajectory Judge**: Are tool calls appropriate?
- **Tool Efficiency**: Ratio of expected/actual tool calls

## Solutions demonstrated
- **Context compression** via tool consolitation and pruning
- **Context selection** via prompt routing


### 2. [TODO: Context Distraction]

- 

### 3. [TODO: Context Clash]

- 

### 4. [TODO: Context Poisoning]


### 5. [TODO: Context Isolation]

-


```bash
# Install dependencies
uv sync

# Set environment variables
cp .env.example .env  # Add your ANTHROPIC_API_KEY and LANGSMITH_API_KEY

# Run the notebook
jupyter notebook context_confusion_demo.ipynb
```


## Structure

```
context_confusion/
├── tools.py              # 75 tools including confusing near-duplicates
├── instructions.py       # Simple base instructions
├── additional_context.py # Irrelevant domain instructions for Problem 3
└── resources/            # Mock data (orders, customers, carriers, warehouses)

context_confusion_demo.ipynb  # context confusion demonstration notebook
```

