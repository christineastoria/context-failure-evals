# Context Management with LangSmith Evaluations

Context engineering is controlling what makes it into your prompt. Managing context incorrectly can lead to bugs and unexpected behaviors. This repository demonstrates common context management pitfalls and how to use LangSmith to evaluate, iterate, and develop better strategies for building more reliable agents.

<img width="857" height="386" alt="Screenshot 2025-12-20 at 8 27 22 AM" src="https://github.com/user-attachments/assets/dab73fd5-bb04-4257-972f-cc7c31e663b1" />


## Setup

```bash
# Install dependencies
uv sync

# Set environment variables
cp .env.example .env  # Add your ANTHROPIC_API_KEY and LANGSMITH_API_KEY

# Run notebooks
jupyter notebook notebooks/
```

## Structure

```
context-failure-evals/
├── notebooks/
│   ├── context_confusion_demo.ipynb     # Context confusion demonstration
│   └── context_distraction_demo.ipynb   # Context distraction demonstration
├── context_confusion/
│   ├── tools.py                          # 75 tools including near-duplicates
│   ├── instructions.py                   # Base instructions
│   ├── additional_context.py             # Irrelevant domain instructions
│   ├── resources/                        # Mock data and test cases
│   ├── tests/                            # Evaluators and dataset utilities
│   ├── utils/                            # Agent helpers and plotting utilities
│   └── solutions/                        # Consolidated tools and solutions
└── context_distraction/
    ├── agent.py                          # Standard ReAct agent
    ├── graph.py                          # Graph agent with context isolation
    ├── resources/                        # Mock APIs and test tasks
    ├── tests/                            # Evaluators and dataset utilities
    └── debug/                            # Claude Code debugging utilities
```


## Notebooks

### 1. Context Confusion (`notebooks/context_confusion_demo.ipynb`)

Demonstrates how **context confusion** - superfluous context from excessive tools, verbose instructions, and irrelevant information - degrades LLM agent performance.

**The Problem:** The Berkeley Function-Calling Leaderboard shows **every model performs worse with more tools**. Too much in the context leads to poor tool selection, unnecessary calls, and incorrect responses.

**Three problems measured with trajectory-based evaluation:**
1. **Tool Overload** - ~75 tools → confusion and poor selection
2. **Irrelevant Noise** - Unrelated tools distract even at moderate counts  
3. **Instruction Bloat** - Verbose multi-domain instructions reduce focus

**Evaluators:**
- **Trajectory Match**: Do tool calls match expected tools?
- **Success Criteria**: Is the response accurate and complete?
- **LLM Trajectory Judge**: Are tool calls appropriate?
- **Tool Efficiency**: Ratio of expected/actual tool calls

**Solutions demonstrated:**
- Context compression via tool consolidation and pruning
- Context selection via prompt routing

### 2. Context Distraction (`notebooks/context_distraction_demo.ipynb`)

Demonstrates how **context distraction** - accumulated tool call results over long task sequences - degrades recall accuracy in complex, multi-step research tasks.

**The Problem:** As agents perform complex tasks with many operations, each tool call and result accumulates in the conversation context. Research shows LLMs struggle to maintain recall accuracy over very long contexts.

**Evaluators:**
- **Recall Accuracy**: Does the agent correctly recall facts from throughout the task?
- **Tool Call Completeness**: Are all expected research steps executed?
- **Tool Call Efficiency**: Ratio of expected to actual tool calls

**Solutions demonstrated:**
- Context isolation via supervisor/researcher pattern
- Reflection tools for maintaining plans over long tasks
- Explicit information passing between nodes

**Debugging utilities:** Includes Claude Code debugging scripts in `context_distraction/debug/` for inspecting traces and agent behavior

### 3. Context Clash

*Coming soon*

### 4. Context Poisoning

*Coming soon*

### 5. Context Isolation

*Coming soon*

