
import requests, sys, json

BASE = sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8080"

ENDPOINTS = [
    "/api/public/v1/health",
    "/api/public/v1/routes_summary",
    "/master_path/v3/start/test",
    "/objections/v3/start/test",
    "/upsell/v3/start/test",
    "/arena/v4/start/test",
    "/sleeping_dragon/v4/start/test",
    "/exam/v2/start/test",
    "/mini/v3/health",
    "/crm/v4/health",
    "/crm_sync/v1/health",
    "/integrations/v4/payment/create"
]

def main():
    results = {}
    for ep in ENDPOINTS:
        url = BASE + ep
        try:
            if ep.endswith("/payment/create"):
                r = requests.post(url, json={"amount": 10, "currency": "KGS"}, timeout=10)
            elif "/start/" in ep:
                r = requests.post(url, timeout=10)
            else:
                r = requests.get(url, timeout=10)
            results[ep] = {"ok": r.ok, "status": r.status_code}
        except Exception as e:
            results[ep] = {"ok": False, "error": str(e)}
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
