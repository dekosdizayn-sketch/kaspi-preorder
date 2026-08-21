import xml.etree.ElementTree as ET
from pathlib import Path

XML_FILE = Path("ACTIVE_preorder1.xml")

print("DEKOS Kaspi Automation іске қосылды")

if not XML_FILE.exists():
    raise FileNotFoundError(f"Файл табылмады: {XML_FILE}")

tree = ET.parse(XML_FILE)
root = tree.getroot()

updated = 0
skipped = 0

for offer in root.iter():
    if not offer.tag.endswith("offer"):
        continue

    availability = None
    for child in offer.iter():
        if child.tag.endswith("availability"):
            availability = child
            break

    if availability is None:
        skipped += 1
        continue

    if availability.get("preOrder") != "1":
        availability.set("preOrder", "1")
        updated += 1

# Kaspi feed: барлық табылған тауарлар 1 күндік предзаказға қойылады.
tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

print(f"Жаңартылған тауар: {updated}")
print(f"Availability жоқ тауар: {skipped}")
print("Барлық тауар 1 күндік предзаказға қойылды")
