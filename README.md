# 🏦 Finance Intelligence Copilot

> **Production-grade AI copilot for finance professionals.**
> Version 1 — Interview Intelligence.

---

## What It Does

Speak or type a finance interview question. The system will:

1. **Transcribe** your audio in real time (Faster Whisper)
2. **Classify** the question category (Gemini)
3. **Retrieve** relevant finance knowledge (markdown knowledge base)
4. **Generate** an institutional-quality answer (Gemini)
5. **Predict** likely follow-up questions (Gemini)
6. **Score** answer confidence, completeness, and accuracy (Gemini)

Results appear instantly on a professional dashboard.

---

## Architecture

```
Audio/Text → Listener → Context → Interview → Knowledge → Expert → Follow-Up → Evaluation → Dashboard
                Agent     Agent     Agent       Agent       Agent     Agent        Agent
```

### Agents

| Agent | Purpose | Uses LLM? |
|---|---|---|
| **Listener** | Audio → transcript | No (Whisper) |
| **Context** | Session history enrichment | No (pure logic) |
| **Interview** | Question classification | Yes |
| **Knowledge** | Markdown retrieval | No (keyword search) |
| **Finance Expert** | Answer generation | Yes |
| **Follow-Up** | Follow-up prediction | Yes |
| **Evaluation** | Quality scoring | Yes |

### Technology Stack

- **Language**: Python 3.10+
- **Frontend**: Streamlit
- **Speech-to-Text**: Faster Whisper
- **LLM**: Google Gemini (via `google-genai` SDK)
- **Data Validation**: Pydantic v2
- **Testing**: Pytest

---

## Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd finance-intelligent-copilot
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and add your Google Gemini API key:
```
GEMINI_API_KEY=your-actual-api-key-here
```

Get a free API key at: https://aistudio.google.com/apikey

### 5. Launch

```bash
streamlit run app/main.py
```

The dashboard opens at `http://localhost:8501`.

---

## Usage

### Voice Input
1. Click the microphone button
2. Speak your interview question clearly
3. Stop recording — the pipeline runs automatically

### Text Input
1. Type your question in the text box
2. Click **Submit Question**

### Session Memory
The system remembers your questions within a session. Later answers are contextually aware of earlier questions. Click **Clear Session** in the sidebar to reset.

---

## Demo Scenarios

Try these questions to see the system in action:

### Valuation
- "Walk me through a DCF analysis"
- "What is the difference between enterprise value and equity value?"
- "When would you use an LBO model?"

### Accounting
- "Walk me through the three financial statements"
- "If depreciation increases by $10, walk me through the impact on all three statements"
- "What is deferred revenue?"

### Markets
- "If interest rates rise, what happens to bond prices?"
- "Explain put-call parity"
- "What does an inverted yield curve signal?"

### Behavioral
- "Why investment banking?"
- "Tell me about a time you showed leadership"
- "Walk me through your resume"

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run With Coverage

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/test_knowledge_agent.py -v
pytest tests/test_orchestrator.py -v
```

---

## Project Structure

```
finance-intelligent-copilot/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Streamlit entry point
│   ├── core/
│   │   ├── config.py                # Environment & settings (Pydantic)
│   │   ├── logging_config.py        # Centralised logging
│   │   ├── models.py                # All domain models (Pydantic)
│   │   ├── session.py               # Session memory
│   │   ├── llm_client.py            # Gemini API wrapper
│   │   └── speech_client.py         # Faster Whisper wrapper
│   ├── agents/
│   │   ├── listener_agent.py        # Audio → transcript
│   │   ├── context_agent.py         # Session enrichment
│   │   ├── interview_agent.py       # Question classification
│   │   ├── knowledge_agent.py       # Knowledge retrieval
│   │   ├── finance_expert_agent.py  # Answer generation
│   │   ├── follow_up_agent.py       # Follow-up prediction
│   │   ├── evaluation_agent.py      # Quality scoring
│   │   └── orchestrator.py          # Pipeline coordinator
│   ├── prompts/
│   │   ├── classification_prompt.txt
│   │   ├── finance_expert_prompt.txt
│   │   ├── followup_prompt.txt
│   │   └── evaluation_prompt.txt
│   └── ui/
│       └── dashboard.py             # Streamlit dashboard
├── knowledge/
│   ├── valuation.md
│   ├── accounting.md
│   ├── equity_research.md
│   ├── markets.md
│   ├── behavioral.md
│   └── interview_questions.md
├── logs/                            # Runtime log output
├── tests/
│   ├── conftest.py                  # Shared fixtures
│   ├── test_models.py
│   ├── test_llm_client.py
│   ├── test_listener_agent.py
│   ├── test_context_agent.py
│   ├── test_interview_agent.py
│   ├── test_knowledge_agent.py
│   ├── test_finance_expert_agent.py
│   ├── test_follow_up_agent.py
│   ├── test_evaluation_agent.py
│   └── test_orchestrator.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Configuration

All settings are configured via the `.env` file:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model identifier |
| `WHISPER_MODEL_SIZE` | `base` | Whisper model (tiny/base/small/medium/large-v3) |
| `WHISPER_DEVICE` | `cpu` | Compute device (cpu/cuda) |
| `WHISPER_COMPUTE_TYPE` | `int8` | Quantisation (int8/float16/float32) |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Performance Tips

- **Faster transcription**: Use `WHISPER_MODEL_SIZE=tiny` for speed, `large-v3` for accuracy
- **GPU acceleration**: Set `WHISPER_DEVICE=cuda` and `WHISPER_COMPUTE_TYPE=float16` if CUDA is available
- **Lower latency LLM**: `gemini-2.0-flash` is optimised for speed; switch to `gemini-2.5-pro` for quality

---

## Known Limitations

1. **Audio recording** requires `audio-recorder-streamlit`; falls back to file upload if unavailable
2. **Knowledge retrieval** uses keyword matching (V1); future versions will use vector search
3. **Session memory** is in-process only — restarting the app clears history
4. **Whisper model loading** takes 5-30 seconds on first transcription
5. **No authentication** — this is a local-first tool, not a multi-tenant SaaS

---

## Future Roadmap

The architecture is designed to support these future product modes:

- [x] **Interview Intelligence** (shipped in V1)
- [ ] Equity Research Coach
- [ ] Stock Pitch Assistant
- [ ] Valuation Coach
- [ ] Accounting Coach
- [ ] Earnings Call Intelligence
- [ ] Market Intelligence

Each mode will plug into the same agent pipeline with mode-specific prompts, knowledge, and evaluation criteria.

---

## License

Proprietary. All rights reserved.
