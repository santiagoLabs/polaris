# Polaris

Try it here: https://polaris-vercel-nine.vercel.app/

**Multi-Agent Crisis Response Simulation**

Polaris models how different world leader archetypes might respond to geopolitical crises. Using RAG (Retrieval-Augmented Generation) and concurrent AI agents, it simulates reactions from four distinct leadership personalities, each with unique traits that influence their decision-making.

## How It Works

```
Event Input → Vector Embedding → Similar Historical Events (RAG)
                                         ↓
                              4 Leader Agents (concurrent)
                                         ↓
                              Escalation Scores + Reactions
```

1. **You describe a crisis** — e.g., "China announces naval exercises near Taiwan"
2. **RAG finds context** — Similar historical events are retrieved via vector similarity search
3. **Agents reason** — Four AI leaders analyze the event through their personality lens
4. **Results returned** — Each leader provides an escalation score (0-10), reaction, and rationale

## Leader Archetypes

| Archetype | Traits |
|-----------|--------|
| **Revisionist Expansionist** | High aggression, low diplomacy, high risk tolerance |
| **Status-quo Diplomat** | Low aggression, high diplomacy, low risk tolerance |
| **Crisis Populist** | Medium aggression, volatile based on domestic pressure |
| **Isolationist Stabilizer** | Low aggression, low risk tolerance, prioritizes stability |

## Tech Stack

- **Backend**: Python + FastAPI (fully async)
- **Database**: PostgreSQL + pgvector (1536-dim embeddings)
- **LLM**: Anthropic Claude for agent reasoning
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: React + Vite
- **Hosting**: Render (API) + Vercel (UI) + Supabase (DB)

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL with pgvector extension (or Supabase account)

### Backend Setup

```bash
# Clone and enter project
cd polaris

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys:
#   DATABASE_URL=postgresql://...
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...

# Run the API
uvicorn app.main:app --reload
```

API available at `http://localhost:8000` (docs at `/docs`)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`

## API Endpoints

### `POST /api/simulate`

Run a crisis simulation.

```json
// Request
{ "text": "North Korea tests intercontinental ballistic missile" }

// Response
{
  "simulation_id": "uuid",
  "event_text": "...",
  "results": [
    {
      "leader": "Revisionist Expansionist",
      "escalation_score": 7.5,
      "reaction": "Condemn the test while accelerating own missile program",
      "rationale": "...",
      "similar_events": [...]
    }
  ]
}
```

### `GET /api/leaders`

Get all leader archetype profiles with their trait scores.

### `GET /api/history`

Get past simulations with average escalation scores.

## Database Schema

```sql
-- Events with vector embeddings for similarity search
events (id, text, embedding vector(1536), created_at)

-- Leader personality traits (0-10 scale)
leader_profiles (id, name, aggression, diplomacy, risk_tolerance,
                 domestic_pressure, escalation_threshold)

-- Simulation runs
simulations (id, event_id, created_at)

-- Per-leader results
leader_sim_results (id, simulation_id, leader_id, escalation_score,
                    reaction, rationale)
```

## Project Structure

```
polaris/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/routes.py        # API endpoints
│   ├── agents/
│   │   ├── coordinator.py   # Spawns agents concurrently
│   │   └── leader_agent.py  # Claude-powered leader logic
│   ├── db/
│   │   └── connection.py    # Async PostgreSQL pool
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── embeddings.py    # OpenAI embedding service
│       └── vector_search.py # pgvector similarity search
├── frontend/
│   └── src/
│       ├── App.jsx          # Main React component
│       └── App.css          # Styles
├── requirements.txt
└── render.yaml              # Render deployment config
```

## Deployment

### Backend (Render)

1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set environment variables: `DATABASE_URL`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
4. Render auto-detects `render.yaml` configuration

### Frontend (Vercel)

1. Connect your GitHub repo to Vercel
2. Set root directory to `frontend`
3. Add environment variable: `VITE_API_URL=https://your-render-app.onrender.com/api`
4. Deploy

### Database (Supabase)

1. Create a new Supabase project
2. Enable pgvector extension
3. Run the schema migrations
4. Use the connection string in `DATABASE_URL`

## Concepts Learned

This project covers:

- **FastAPI** — Async Python web framework with automatic OpenAPI docs
- **pgvector** — PostgreSQL extension for vector similarity search
- **RAG** — Retrieval-Augmented Generation for grounding LLM responses
- **Multi-agent systems** — Concurrent AI agents with distinct personalities
- **Embeddings** — Converting text to semantic vectors for similarity search

## License

MIT
