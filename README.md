# Multi-llama 🧠🦙

A minimal but working multi-agent LLM orchestrator in Python, powered by Ollama.

## Overview

Multi-llama implements an intelligent multi-agent system with:
- **One coordinator agent** (the "brain") that:
  - Dynamically defines specialized worker agents (up to 5) tailored to each task
  - Plans and delegates subtasks
  - Evaluates results for quality
  - Iterates to improve results (up to 5 iterations)
  - Aggregates final answers
- **Dynamic worker agents** (specialists) created on-demand with custom capabilities
- **In-memory task graph** with dependency tracking
- **Iterative self-improvement** - the system refines its output until satisfactory
- **Simple CLI** to run tasks from user prompts

## Architecture

### Core Components

1. **Task Dataclass** (`Task`)
   - `id`: Unique task identifier
   - `parent_id`: Parent task reference
   - `description`: Task description
   - `assigned_agent`: Which agent executes it
   - `status`: `PENDING` | `RUNNING` | `DONE` | `FAILED`
   - `depends_on`: List of task IDs this depends on
   - `output`: Full LLM response
   - `summary`: Truncated summary for context passing

2. **LLM Wrapper** (Ollama)
   - `call_llm()`: Basic chat completion
   - `call_llm_json()`: JSON-mode with automatic retry on parse failure

3. **Agent System**
   - `Agent`: Base class with system prompt and execution logic
   - `coordinator`: Central intelligence that:
     - Defines specialized workers for each task
     - Plans subtasks and delegates work
     - Evaluates result quality
     - Iterates to improve results
   - **Dynamic workers**: Created on-demand with custom:
     - Names (e.g., `kid_explainer`, `HaikuCraftsman`, `code_analyst`)
     - Roles and expertise areas
     - System prompts tailored to the specific task

4. **Orchestrator Loop**
   - Creates root task from user prompt
   - **Iteration loop** (up to 5 iterations):
     - Coordinator analyzes task and defines specialized workers
     - Creates dynamic worker agents
     - Plans subtasks for defined workers
     - Executes tasks when dependencies are satisfied
     - Aggregates results
     - **Evaluates result quality**
     - If unsatisfactory: defines new workers and iterates
     - If satisfactory: returns final answer

### Task Flow

```
User Prompt
    ↓
Root Task (coordinator)
    ↓
╔═══════════════════ ITERATION LOOP (max 5) ═══════════════════╗
║  [Worker Definition Phase]                                     ║
║  Coordinator analyzes task → Defines 1-5 specialized workers  ║
║    ↓                                                           ║
║  [Dynamic Agent Creation]                                      ║
║  Create workers: kid_explainer, phd_explainer, etc.           ║
║    ↓                                                           ║
║  [Planning Phase]                                              ║
║  Coordinator plans subtasks for workers                        ║
║    ↓                                                           ║
║  [Execution Phase]                                             ║
║  Worker 1 → Worker 2 → Worker 3 (with dependencies)          ║
║    ↓                                                           ║
║  [Aggregation Phase]                                           ║
║  Coordinator synthesizes results                               ║
║    ↓                                                           ║
║  [Evaluation Phase]                                            ║
║  Is result satisfactory?                                       ║
║    ├─ YES → Return final answer                               ║
║    └─ NO  → Define new workers, iterate again                 ║
╚════════════════════════════════════════════════════════════════╝
    ↓
Final Answer
```

## Requirements

- Python 3.13+ (or 3.11+)
- [Ollama](https://ollama.ai/) running locally
- Model: `gpt-oss` (or configure your preferred model)

## Installation

```bash
# Clone or navigate to the repo
cd Multi-llama

# Install dependencies with uv
uv sync
```

## Usage

### Basic Usage

```bash
uv run python app.py "Your question or task here"
```

### Example

```bash
uv run python app.py "Explain how photosynthesis works in 3 key steps"
```

### Output

The orchestrator will:
1. Show iteration progress (ITERATION 1/5, 2/5, etc.)
2. Log worker definition and creation
3. Show task planning and execution in real-time
4. Display evaluation results (✓ Satisfactory or ✗ Needs improvement)
5. Print the final aggregated answer

```
================================================================================
ITERATION 1/5
================================================================================

Coordinator defining worker agents
Defined 3 workers: ['kid_explainer', 'college_explainer', 'phd_explainer']
Created agent: kid_explainer - Explains complex topics to children
Created agent: college_explainer - Explains to college level
Created agent: phd_explainer - Explains at PhD level
Planned 3 subtasks
Agent 'kid_explainer' executing task: a2b6ba01
Task a2b6ba01 completed successfully
...
Coordinator aggregating 3 subtask results
Coordinator evaluating result quality
Evaluation: ✓ Satisfactory

✅ Result satisfactory after 1 iteration(s)

================================================================================
FINAL ANSWER
================================================================================
[Final markdown-formatted answer]
================================================================================
```

## Configuration

### Change Model

Edit the model name in `app.py`:

```python
def call_llm(messages: list[dict], model: str = "your-model-name") -> str:
    ...
```

### Adjust Logging Level

```python
logger.add(sys.stderr, level="DEBUG", format="...")
```

Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Customize Coordinator Behavior

You can adjust the coordinator's decision-making by modifying its system prompt in `create_coordinator_agent()`. For example:

- **Change worker limit**: Modify "up to 5" workers to a different number
- **Add domain expertise**: Include specific domain knowledge in the prompt
- **Adjust evaluation criteria**: Change what the coordinator considers "satisfactory"
- **Modify iteration strategy**: Guide how the coordinator improves results

### Safety Limits

- Maximum 5 main iterations (worker definition → execution → evaluation cycles)
- Maximum 50 task execution iterations per main iteration
- Maximum 5 workers per iteration
- Prevents infinite loops and runaway costs

### Dependencies

Tasks can depend on other tasks:

```json
{
  "subtasks": [
    {
      "description": "Research topic X",
      "assigned_agent": "research_worker",
      "depends_on": []
    },
    {
      "description": "Write summary using research",
      "assigned_agent": "writer_worker",
      "depends_on": ["<id_of_first_task>"]
    }
  ]
}
```

The orchestrator only executes tasks when all dependencies are `DONE`.