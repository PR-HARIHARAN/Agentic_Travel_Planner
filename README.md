# AI Trip Planner

## Overview

AI Trip Planner is an agent-based travel planning application that combines a FastAPI backend, a Streamlit frontend, and LangGraph-powered tool calling to generate travel plans. It is designed for users who want destination ideas, weather information, attraction and restaurant suggestions, transportation guidance, and trip cost estimates in one place.

The app accepts a natural-language travel request, routes it through an LLM-driven agent, and uses external tools to gather supporting data before returning a markdown-formatted travel plan. The frontend also renders a simple execution trace so users can see which tools were called during planning.

## Features

- Natural-language trip planning requests
- Agentic orchestration with LangGraph tool calling
- Weather lookup using OpenWeatherMap
- Attraction, restaurant, activity, and transportation search using Google Places with Tavily fallback
- Currency conversion support
- Hotel cost, total expense, and daily budget calculations
- FastAPI backend endpoint for programmatic access
- Streamlit UI for interactive trip planning and execution trace display

## Tech Stack

- Language: Python
- Backend framework: FastAPI
- Frontend framework: Streamlit
- Agent orchestration: LangGraph, LangChain
- LLM providers: Groq, OpenAI
- Search and location tools: Google Places, Tavily Search
- Weather data: OpenWeatherMap API
- Configuration: YAML, `.env`
- HTTP clients: `requests`, FastAPI middleware and responses

## Architecture

This project uses a two-part architecture:

1. A FastAPI backend exposed in [main.py](main.py) that accepts travel questions at `POST /query` and returns the generated answer plus an execution trace.
2. A Streamlit frontend in [streamlit_app.py](streamlit_app.py) that sends user prompts to the backend, displays the generated travel plan, and shows the agent activity trace.

At the core is an agent workflow defined in [agent/agentic_workflow.py](agent/agentic_workflow.py). The workflow builds a LangGraph state machine with:

- a system prompt that instructs the agent to act as a travel planner,
- an LLM loaded through [utils/model_loader.py](utils/model_loader.py),
- a set of tools for weather, place search, currency conversion, and trip cost calculations.

The tool layer is split across small wrappers in `tools/` and their implementation helpers in `utils/`:

- weather tools query OpenWeatherMap,
- place search tools query Google Places and fall back to Tavily when needed,
- calculator tools compute trip totals and daily budgets,
- currency tools convert amounts between currencies.

The project does not define a database or persistent storage layer.

## Installation

1. Install Python 3.12 or later, as required by [pyproject.toml](pyproject.toml).
2. Clone the repository and open the project folder.
3. Create and activate a virtual environment.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

If you prefer the project metadata file, you can also install from the package configuration defined in [pyproject.toml](pyproject.toml).

5. Create a `.env` file in the project root with the required API keys.

## Usage

Start the backend:

```bash
uvicorn main:app --reload
```

Start the Streamlit app in a separate terminal:

```bash
streamlit run streamlit_app.py
```

Then open the Streamlit app in your browser and enter a travel prompt such as:

```text
Plan a 5-day trip to Goa for two adults with a medium budget.
```

The frontend sends the request to `POST /query` on `http://localhost:8000`, receives the generated itinerary, and renders the response along with the agent trace.

### Backend API

`POST /query`

Request body:

```json
{
	"question": "Plan a trip to Goa for 5 days"
}
```

Successful response format:

```json
{
	"answer": "...",
	"agent_trace": [
		{
			"stage": "input",
			"label": "User Request",
			"detail": "Plan a trip to Goa for 5 days"
		}
	]
}
```

If an error occurs, the API returns a JSON error response with status code `500`.

## Project Structure

- [main.py](main.py): FastAPI application and `/query` endpoint
- [streamlit_app.py](streamlit_app.py): Streamlit UI for interacting with the backend
- [agent/](agent): LangGraph agent construction and workflow orchestration
- [prompt_library/](prompt_library): System prompt used by the agent
- [tools/](tools): LangChain tool wrappers for weather, search, currency, and expense calculations
- [utils/](utils): Implementation helpers for APIs, model loading, and calculations
- [config/config.yaml](config/config.yaml): Model provider and model name configuration
- [requirements.txt](requirements.txt): Python dependency list
- [pyproject.toml](pyproject.toml): Project metadata and dependency declarations
- [notebook/](notebook): Notebook experiments and exploratory work

## Configuration

The application loads environment variables with `python-dotenv` and expects the following keys to be available when their related tools are used:

- `GROQ_API_KEY`: used when the model provider is set to Groq
- `OPENAI_API_KEY`: used when the model provider is set to OpenAI
- `OPENWEATHERMAP_API_KEY`: used by the weather tools
- `GPLACES_API_KEY`: used by the Google Places tools
- `EXCHANGE_RATE_API_KEY`: used by the currency conversion tool

Model selection is defined in [config/config.yaml](config/config.yaml):

```yaml
llm:
	openai:
		provider: "openai"
		model_name: "o4-mini"
	groq:
		provider: "groq"
		model_name: "qwen/qwen3-32b"
```

The backend currently instantiates the agent with `model_provider="groq"` in [main.py](main.py), so Groq credentials are assumed by default.

## API Documentation

### `POST /query`

Accepts a travel-planning question and returns the final answer plus a simplified execution trace.

Request example:

```bash
curl -X POST http://localhost:8000/query \
	-H "Content-Type: application/json" \
	-d '{"question":"Plan a trip to Kerala for 4 days"}'
```

Response example:

```json
{
	"answer": "...final travel plan in markdown...",
	"agent_trace": [
		{
			"stage": "input",
			"label": "User Request",
			"detail": "Plan a trip to Kerala for 4 days"
		},
		{
			"stage": "tool-call",
			"label": "Calling search_attractions",
			"detail": "{\"place\": \"Kerala\"}"
		}
	]
}
```

## Examples

Example user prompts:

```text
Plan a budget trip to Goa for 3 days.
```

```text
Create a family travel plan for Manali with hotel, food, transport, and weather details.
```

Typical output includes a markdown travel plan with itinerary suggestions, hotel estimates, attractions, restaurants, activities, transportation options, weather, and cost breakdowns. Exact results depend on the live model output and the availability of external APIs.

## Contributing

Contributions are welcome. Keep changes focused, follow the existing project structure, and avoid introducing breaking changes to the backend API or Streamlit workflow unless they are documented. When adding new tools or integrations, update the README and configuration notes accordingly.

Before opening a pull request, verify the application still runs locally and that any new environment variables, dependencies, or prompts are documented.

## Future Improvements

- Add persistent conversation history and saved trip plans
- Expose additional API endpoints for health checks and model/tool status
- Add input validation and clearer error messages for missing API keys
- Support a configurable model provider instead of hardcoding Groq in the backend
- Add automated tests for the agent workflow and tool wrappers
- Improve the Streamlit UI with saved itineraries and downloadable outputs
