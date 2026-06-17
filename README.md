# AI Multi-Agent Travel Planner

A production-quality web application built using **LangGraph**, **LangChain**, and **Streamlit** that coordinates a team of specialized AI agents to generate comprehensive, personalized travel itineraries.

---

## 🏗️ System Architecture

The workflow is modeled as a stateful graph using LangGraph. It starts with user details, processes destination characteristics, runs searches in parallel (flights, lodging, weather), aggregates the details, and publishes a consolidated travel document.

```
                  [ START ]
                      │
           [destination_extraction]
             /        │       \
      [flight_agent]  │  [weather_agent]  (Parallel Execution)
             \        │       /
             [hotel_agent] 
             /        │       \
             \        │       /
            [itinerary_generator]         (Fan-in / Merge Point)
                      │
               [final_planner]
                      │
                   [ END ]
```

### Specialized Agents
1. **Destination Extraction Agent:** Normalizes city/country names, calculates trip length, and computes budget tiers.
2. **Flight Agent:** Finds flights matching routes and budget, providing custom recommendations.
3. **Hotel Agent:** Recommends top lodgings and aligns them with user style preferences.
4. **Weather Agent:** Evaluates travel season forecasts and customizes a packing checklist.
5. **Itinerary Generator Agent:** Fans-in flight, hotel, and climate details, crafting a custom day-by-day activity calendar.
6. **Final Planner Agent:** Integrates and structures all pieces into a single, cohesive, download-ready Markdown brochure.

---

## 📁 Project Structure

```
travel-planner/
│
├── app.py               # Streamlit application containing the UI layouts and streaming events
├── graph.py             # LangGraph workflow definition and state-machine compilation
├── state.py             # TypedDict definitions with list reducers for execution logs
│
├── agents/              # Core Agent node implementations
│     ├── destination_agent.py
│     ├── flight_agent.py
│     ├── hotel_agent.py
│     ├── weather_agent.py
│     ├── itinerary_agent.py
│     └── final_planner.py
│
├── tools/               # Query layers supporting simulation and API connections
│     ├── flight_tool.py
│     ├── hotel_tool.py
│     └── weather_tool.py
│
├── requirements.txt     # Python project dependencies
└── README.md            # Execution manual and overview documentation
```

---

## ⚡ Setup & Run Instructions

### Prerequisites
* Python 3.10 or higher installed.

### 1. Install Dependencies
In your command terminal, run:
```bash
pip install -r requirements.txt
```

### 2. Start the Application
Run the Streamlit server:
```bash
streamlit run app.py
```

### 3. Open in Browser
The browser will automatically open to `http://localhost:8501`. If it doesn't, navigate there manually.

---

## 🤖 Agent Execution Modes

The planner operates in two distinct modes depending on your API configuration:

1. **Simulation Mode (Default / Offline)**:
   * Runs immediately out of the box with **no API keys required**.
   * Employs deterministic lookup databases and procedural generators to simulate agent tool results and recommendations (clearly labeled).
2. **LLM Hybrid Mode (Online)**:
   * Activated by pasting an `OPENAI_API_KEY` in the Streamlit Sidebar.
   * Leverages `gpt-4o-mini` to dynamically parse destination details, score hotels against custom text descriptions, build personalized packing advice, and narrate custom itineraries.

---

## 📋 Example Input & Output Trace

### Example Input
* **Source City**: `New York`
* **Destination City**: `London, UK`
* **Departure Date**: `2026-07-02`
* **Return Date**: `2026-07-07` (5 Days)
* **Total Budget**: `$3000 USD`
* **Preferences**: `vegan food, museums, classic tea, walking tour`

### Example Execution Logs (Trace)
```text
Planner: Starting travel graph execution.
Destination Extraction Agent (LLM): Extracted 'London, United Kingdom' starting from 'New York'. Mode: Mid-range.
Flight Agent: Retrieved 3 flights from New York to London. (Reasoning enhanced by OpenAI)
Hotel Agent: Found 3 hotels in London matching budget category. (Preferences matched by OpenAI)
Weather Agent: Fetched weather for London in July. Expecting: Pleasant & Clear. (Packing suggestions refined by OpenAI)
Itinerary Agent: Creating a 5-day itinerary for London. (Generated dynamically by OpenAI)
Final Planner Agent: Compiled flight, hotel, weather, and itinerary details into Markdown. (Copy-writing and formatting enhanced by OpenAI)
```
