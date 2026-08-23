import os
import xml.etree.ElementTree as ET
from pathlib import Path

XML_FILE = Path("ACTIVE_preorder1.xml")
EXPECTED_COMPANY = "30457864"
EXPECTED_MERCHANT = "30457864"
EXPECTED_OFFERS = 50
TARGET_PREORDER = "2"

def local(tag):
    return tag.rsplit("}", 1)[-1]

if not XML_FILE.exists():
    raise FileNotFoundError(f"Файл табылмады: {XML_FILE}")

tree = ET.parse(XML_FILE)
root = tree.getroot()
company = next((e.text.strip() for e in root.iter() if local(e.tag) == "company" and (e.text or "").strip()), "")
merchant = next((e.text.strip() for e in root.iter() if local(e.tag) == "merchantid" and (e.text or "").strip()), "")

offers = []
seen_sku = set()
for offer in root.iter():
    if local(offer.tag) != "offer":
        continue
    sku = (offer.get("sku") or "").strip()
    if not sku or sku in seen_sku:
        continue
    seen_sku.add(sku)
    offers.append(offer)

summary = {
    "company": company,
    "merchant": merchant,
    "total": len(offers),
    "updated": 0,
    "already_preorder": 0,
    "skipped": 0,
}

# Қатаң қауіпсіздік: тек дәл осы магазиннің дәл 50 тауарлық XML-і.
if company != EXPECTED_COMPANY or merchant != EXPECTED_MERCHANT or len(offers) != EXPECTED_OFFERS:
    print(f"ҚАУІПСІЗДІК ТОҚТАТУЫ: Company={company}, Merchant={merchant}, Тауар={len(offers)}")
    print(f"Күтілгені: Company={EXPECTED_COMPANY}, Merchant={EXPECTED_MERCHANT}, Тауар={EXPECTED_OFFERS}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            for k, v in summary.items():
                f.write(f"{k}={v}\n")
            f.write("blocked=true\n")
    raise SystemExit(2)

for offer in offers:
    availability = next((e for e in offer.iter() if local(e.tag) == "availability"), None)
    if availability is None or availability.get("available") != "yes":
        summary["skipped"] += 1
        continue
    if availability.get("preOrder") == TARGET_PREORDER:
        summary["already_preorder"] += 1
    else:
        availability.set("preOrder", TARGET_PREORDER)
        summary["updated"] += 1

tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)
for k, v in summary.items():
    print(f"{k}: {v}")

out = os.environ.get("GITHUB_OUTPUT")
if out:
    with open(out, "a", encoding="utf-8") as f:
        for k, v in summary.items():
            f.write(f"{k}={v}\n")
        f.write("blocked=false\n")

# Manual test trigger: verify GitHub Actions and Telegram notification.
