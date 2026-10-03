"""Run from the project folder:  python check_api.py
Shows what the DONKI API really returns for each endpoint."""
from datetime import date, timedelta

import requests

from src.data.donki_client import BASE_URL

end, start = date.today(), date.today() - timedelta(days=7)
print("Base URL:", BASE_URL)
for ep in ("FLR", "CME", "GST"):
    r = requests.get(f"{BASE_URL}/{ep}", params={"startDate": start.isoformat(), "endDate": end.isoformat()}, timeout=20)
    kind = "JSON" if r.text.strip()[:1] in "[{" else ("EMPTY" if not r.text.strip() else "NOT JSON")
    n = len(r.json()) if kind == "JSON" else "-"
    print(f"{ep}: HTTP {r.status_code} | {kind} | events: {n} | redirects: {len(r.history)} | final url: {r.url[:90]}")
    if kind == "NOT JSON":
        print("   body starts:", repr(r.text[:80]))