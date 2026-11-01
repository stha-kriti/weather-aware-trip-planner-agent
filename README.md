# Weather-Aware Trip Planner Agent

A small tool-calling AI agent that plans a short city trip around the real weather forecast. It looks up the
city, fetches the forecast, and puts outdoor activities on dry days and indoor ones on wet days.

```
request -> LLM decides -> geocode_city("Lisbon") -> LLM decides -> get_forecast(lat, lon, days)
                                                                         |
                                  Markdown plan <- LLM writes plan from the real numbers
```

- **Two chained tools.** The forecast tool needs coordinates from the geocoding tool, so the model must work out the order itself.
- **No framework.** The agent loop is about 15 lines in `src/agent.py`, so every step is visible.
- **Azure OpenAI.** Configured through environment variables; the `model` value is your Azure deployment name.
- **Guardrails.** Step limit with a forced final answer, tool errors returned as text so the model can recover, and a prompt rule to use only numbers returned by the tools.
- **Free data.** Weather and geocoding come from [Open-Meteo](https://open-meteo.com/), no API key needed.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # add your Azure OpenAI endpoint, key, deployment
python src/agent.py examples/request_example.txt      # plan is printed and saved to out/plan.md
pytest                                                # tests need no API key
```

## Limitations

- The forecast covers at most 16 days; for later dates the agent is told to give only a labelled general plan.
- It does not know opening hours or prices and says so.
- Plan quality depends on the model; check details before travelling.

## Ideas for next steps

Add a tool for local events or public-transport times, store past requests to learn preferences, and add an evaluation set of requests with expected behaviour (e.g. rainy day gets an indoor plan).
