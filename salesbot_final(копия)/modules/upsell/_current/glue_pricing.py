
# Optional glue to connect upsell/v3 with pricing computation
try:
    from modules.upsell_pricing_glue.v1 import compute_offer, suggest_upsell
except Exception:
    compute_offer = suggest_upsell = None

DEFAULT_CATALOG = {
  "basic":   {"title":"Basic","items":[{"sku":"song","price":1200}]},
  "premium": {"title":"Premium","items":[{"sku":"song","price":1200},{"sku":"video","price":1800}]},
  "pro":     {"title":"Pro","items":[{"sku":"song","price":1200},{"sku":"video","price":1800},{"sku":"story","price":900}]}
}

def recommend_upgrade(current_tier="basic", target_tier="premium", currency="KGS", discount=0.0, coupon=None, vat=0.0, context=None, catalog=None):
    if not suggest_upsell:
        return {"ok": False, "reason": "upsell_pricing_glue not available"}
    return {"ok": True, "result": suggest_upsell(catalog or DEFAULT_CATALOG, current_tier, target_tier, currency, discount, coupon, vat, context)}
