# Oraklet — Project Study Guide (for ML coursework)

> Paste this whole file into a new chat and say: "This is my project, I'm a beginner learning ML for school, walk me through it topic by topic starting with X." The point of this doc is to give the LLM full context so it can teach *with* the real code instead of inventing a generic toy example.

## 1. What this project actually is

**Oraklet** is a small FastAPI backend that lets a user:
1. Upload a CSV dataset.
2. Get summary statistics for it (`.describe()`).
3. Ask a natural-language question about that dataset, which gets answered by a **local, open-weight LLM** (`HuggingFaceTB/SmolLM2-1.7B-Instruct`, via `transformers.pipeline`) — not an API-based model like GPT.

It is *not* a classic "train a model on data" ML project. It's an **LLM-application** project: the ML system is a pre-trained language model, and the engineering problem is how to feed it context (prompt engineering), parse its output reliably, and reason about its failure modes (hallucination, bias, safety). That distinction matters — say so explicitly to the tutor LLM, because "machine learning" prompts often default to scikit-learn-style supervised learning lessons, which isn't what this repo needs.

## 2. Tech stack

- **Python 3.14**, dependency manager **uv** (`pyproject.toml` + `uv.lock`)
- **FastAPI** — HTTP framework, async endpoints
- **Pydantic v2** — data validation / typed models (`BaseModel`, `Field`, generics)
- **pandas** — CSV parsing and `.describe()` stats
- **transformers + torch** — runs `SmolLM2-1.7B-Instruct` locally via `pipeline("text-generation", ...)`
- **pytest** — unit tests, including `monkeypatch` for mocking the LLM call

## 3. Full file tree (everything that exists — nothing omitted)

```
kk2-oraklet/
├── README.md                  Setup + curl usage instructions (in Swedish)
├── REFLEKTION.md              Author's own security/bias/design reflection
├── pyproject.toml             Dependencies
├── app/
│   ├── main.py                FastAPI app: 4 endpoints
│   ├── config.py               (currently empty — placeholder)
│   ├── data.py                 CSV loading into a module-level pandas DataFrame
│   ├── schemas.py               Pydantic request schema (AskRequest)
│   ├── chain/
│   │   ├── runnable.py         Generic Runnable/RunnableSequence base (LCEL-style pipe pattern)
│   │   ├── steps.py            The 3 pipeline steps: PromptBuilder, LLMRunner, ResponseParser
│   │   └── pipeline.py         Wires the 3 steps into one pipeline: `oraklet = A | B | C`
│   └── tests/
│       ├── test_chain.py       Unit tests for the 3 pipeline steps (LLM step is mocked)
│       └── test_endpoints.py   Integration tests for the FastAPI endpoints
```

That's the whole codebase — 8 real Python files. If a previous chat only mentioned 3, it was likely only describing `chain/` (which *is* the ML-relevant core) and skipping the surrounding app. Both halves matter for a full ML-systems picture: `chain/` is "the model," `main.py`/`data.py`/`schemas.py` is "the product it's embedded in."

## 4. How a request flows through the system (the important diagram)

```
POST /ai/ask  { "question": "..." }
      │
      ▼
main.py: ask()
  - checks a dataset was uploaded (data.dataset is not None)
  - computes data.dataset.describe().to_dict()   ← summary stats, not raw rows
  - builds PromptBuilderInput(question, stats)
  - calls oraklet.invoke(...)
      │
      ▼
chain/pipeline.py:  oraklet = PromptBuilder() | LLMRunner() | ResponseParser()
      │
      ├─▶ Step 1: PromptBuilder.invoke()
      │     loops over stats.items(), builds a short text summary
      │     ("age: mean=30.0, min=18.0, max=65.0\n...")
      │     wraps it in a chat-style message list:
      │       [{"role": "system", "content": "Du är en dataanalytiker..."},
      │        {"role": "user", "content": f"Svara på {stats_summary} ... fråga: {question}"}]
      │
      ├─▶ Step 2: LLMRunner.invoke()
      │     runs the SmolLM2-1.7B pipeline on those chat messages
      │     model returns the FULL conversation back (system+user+assistant turns)
      │     code takes result[0]["generated_text"][-1]["content"]  ← just the assistant's reply
      │
      └─▶ Step 3: ResponseParser.invoke()
            if the model's raw output contains "Svar:", keep only the text after it
            (cheap post-processing to strip the model's "thinking out loud" preamble)
            returns { question, answer, model }
      │
      ▼
JSON response to the client
```

## 5. The `Runnable` pattern (this is the real software-design centerpiece)

`app/chain/runnable.py` is a small hand-rolled version of the pattern LangChain calls "LCEL" (`|` operator chaining, aka the "Chain of Responsibility" / pipeline pattern). Understanding it is worth real study time:

- `Runnable[I, O]` is a generic Pydantic model with one method: `invoke(data: I) -> O`.
- `__or__` (the `|` operator) lets you write `StepA() | StepB() | StepC()` and get back a `RunnableSequence` that runs them in order, feeding each step's output as the next step's input.
- `RunnableSequence.invoke()` is just `self.second.invoke(self.first.invoke(data))` — recursive composition, so chaining N steps costs nothing extra.
- Each step declares its input/output as a distinct Pydantic model (`PromptBuilderOutput`, `LLMRunnerOutput`, etc.), so you get type-checked hand-offs between stages instead of passing around loose dicts.

Good discussion questions for the tutor LLM: *why is this better than one big function? What does "single responsibility" buy you here? What would you have to change if you wanted to add a 4th step (e.g. a safety filter) — and how does that compare to inserting a step into a giant if/else?*

## 6. Where the actual "machine learning" content lives

This project barely touches training — the ML content is entirely about **using** a pretrained model responsibly. That's a legitimate and increasingly common ML topic, but it's a different syllabus than "fit a regression." Concepts actually exercised here:

- **Model selection under resource constraints**: SmolLM2 1.7B chosen over the 135M variant because the smaller one couldn't produce coherent answers at all (documented directly in `REFLEKTION.md`) — a real example of the accuracy/model-size/compute tradeoff.
- **Prompt engineering**: `PromptBuilder` deliberately compresses `data.stats` (which is a full nested dict from `.describe()`) down to `mean/min/max` per column as short text lines, specifically to reduce hallucination by giving the model less to misread. That's context-window/attention management, not just string formatting.
- **Structured chat prompting**: using `role: system/user` message format (the same convention OpenAI/HF chat templates use) instead of one raw string.
- **Output parsing / hallucination mitigation**: `ResponseParser` splitting on a `"Svar:"` (Swedish for "Answer:") marker is a real, common technique for getting a clean answer out of a model that likes to "think out loud" first.
- **Hallucination as an observed failure mode**: the author documented a concrete failure — asking "which country has lowest GDP" and getting back a garbled, dataset-echoing non-answer. Good case study for *why* LLM outputs need validation/guardrails.
- **Bias**: `REFLEKTION.md` explicitly discusses training-data bias (model trained mostly on Swedish/US/UK text skews it toward discussing wealthy countries) — a real example of representation bias in a foundation model, observable through this app's own outputs.
- **Evaluation limits**: the pytest suite (`test_chain.py`) mocks `LLMRunner.invoke` for the "is the pipeline wired correctly" tests — it verifies **data flow**, not **answer quality**. The author explicitly notes this gap. This is a great entry point into discussing *why evaluating LLM output quality is a much harder problem than evaluating deterministic code* (no single "correct" string, need for human eval / LLM-as-judge / rubrics, etc.).

## 7. Security / safety considerations already identified (from `REFLEKTION.md`)

Worth treating as a checklist of "what would you add before shipping this":
- No authentication on any endpoint — anyone can read `/data/stats` (potential PII exposure if a user uploads sensitive CSVs).
- File-upload validation is currently only: extension must be `.csv`, size must be under a hard-coded byte limit (the code comment says 500mb but the intent per REFLEKTION.md was to tighten to 10mb — worth checking `main.py:26-27` for the actual current numbers vs. the reflection notes, they currently disagree).
- No prompt-injection defense: a user could phrase a question to try to override the system prompt ("ignore previous instructions..."), and there's no input sanitization or stronger system-prompt lock-in yet.
- No secrets/API keys in this project (model runs locally), so `.env` leakage isn't a live risk here — but the author reasons about it anyway as general practice.

## 8. Suggested way to use this doc in the next chat

Tell the tutor LLM something like:

> "Here's my actual project. I'm learning ML for school and my last session only looked at 3 files and gave a shallow structure. I want to go deeper. Can you pick one topic at a time from section 6 (prompt engineering, hallucination, bias, evaluation, or model-size tradeoffs) and teach me using this exact code as the example, with questions to check my understanding before moving on?"

That framing forces topic-by-topic depth instead of another generic 3-bullet overview.
