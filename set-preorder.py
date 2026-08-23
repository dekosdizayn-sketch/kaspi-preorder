import os
import xml.etree.ElementTree as ET
from pathlib import Path

XML_FILE = Path("ACTIVE_preorder1.xml")
MAX_EXPECTED_OFFERS = int(os.environ.get("MAX_EXPECTED_OFFERS", "100"))

if not XML_FILE.exists():
    raise FileNotFoundError(f"Файл табылмады: {XML_FILE}")

tree = ET.parse(XML_FILE)
root = tree.getroot()

def local(tag):
    return tag.rsplit("}", 1)[-1]

# XML-дегі нақты магазин ID
company = next((e.text.strip() for e in root.iter() if local(e.tag) == "company" and (e.text or "").strip()), "")
merchant = next((e.text.strip() for e in root.iter() if local(e.tag) == "merchantid" and (e.text or "").strip()), "")

# Тек нақты SKU-ы бар offer-лер есептеледі.
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

actual = len(offers)

summary = {
    "company": company,
    "merchant": merchant,
    "total": actual,
    "updated": 0,
    "already_preorder": 0,
    "skipped": 0,
}

# Қауіпсіздік: сендегі магазин ~50 тауар болғандықтан 699 тауарлық ескі/басқа
# XML-ді автоматты түрде өзгертпейміз. Алдымен дұрыс XML жүктелуі керек.
if actual > MAX_EXPECTED_OFFERS:
    print(f"ҚАУІПСІЗДІК ТОҚТАТУЫ: XML-де {actual} бірегей тауар бар. Лимит: {MAX_EXPECTED_OFFERS}.")
    print(f"Company: {company or '-'}; Merchant: {merchant or '-'}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            for key, value in summary.items():
                f.write(f"{key}={value}\n")
            f.write("blocked=true\n")
    raise SystemExit(2)

for offer in offers:
    availability = next((e for e in offer.iter() if local(e.tag) == "availability"), None)
    if availability is None:
        summary["skipped"] += 1
        continue
    if availability.get("preOrder") != "1":
        availability.set("preOrder", "1")
        summary["updated"] += 1
    else:
        summary["already_preorder"] += 1

tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

for key, value in summary.items():
    print(f"{key}: {value}")

github_output = os.environ.get("GITHUB_OUTPUT")
if github_output:
    with open(github_output, "a", encoding="utf-8") as f:
        for key, value in summary.items():
            f.write(f"{key}={value}\n")
        f.write("blocked=false\n")
