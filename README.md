# SpaceGuard 🛰️

Real-time space weather monitoring dashboard — built for the Nexus Global Talent internship.

Tracks solar flares, CMEs, and geomagnetic storms using NASA's public DONKI API,
and shows a simple, transparent Low/Moderate/High risk status. Monitoring and
visualization first; alerts and forecasting are planned as future work.

## Stack

- Python, Pandas, NumPy — data handling
- Plotly — interactive charts
- Streamlit — dashboard UI
- SQLite — local cache / event history
- NASA DONKI API — data source

## Project structure

```
spaceguard/
├── app.py                  # Streamlit entrypoint (layout only)
├── src/
│   ├── data/                # API client + storage
│   ├── processing/          # cleaning/transform
│   ├── risk/                # risk scoring rules
│   └── viz/                 # chart builders
├── tests/
└── requirements.txt
```

## Running locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then add your real NASA_API_KEY
streamlit run app.py
```

Get a free NASA API key at https://api.nasa.gov (the default `DEMO_KEY` works
but has a very low rate limit).

## Deployment

Deployed via [Streamlit Community Cloud](https://share.streamlit.io):
push to `main` → auto-redeploys. Set `NASA_API_KEY` under the app's
**Settings → Secrets** rather than committing it.

## Status

🚧 In development — following a 20-day roadmap. See project docs for the
full step-by-step plan and risk-scoring methodology.
