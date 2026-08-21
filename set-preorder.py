import os
import xml.etree.ElementTree as ET
from pathlib import Path

XML_FILE = Path("ACTIVE_preorder1.xml")

print("DEKOS Kaspi Automation іске қосылды")

if not XML_FILE.exists():
    raise FileNotFoundError(f"Файл табылмады: {XML_FILE}")

tree = ET.parse(XML_FILE)
root = tree.getroot()

total = 0
updated = 0
already_preorder = 0
skipped = 0

for offer in root.iter():
    if not offer.tag.endswith("offer"):
        continue

    total += 1
    availability = None
    for child in offer.iter():
        if child.tag.endswith("availability"):
            availability = child
            break

    if availability is None:
        skipped += 1
        continue

    if availability.get("preOrder") != "1":
        # Қоймадағы/стоктағы тауарды 1 күндік предзаказға ауыстыру.
        availability.set("preOrder", "1")
        updated += 1
    else:
        already_preorder += 1

tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

summary = {
    "total": total,
    "updated": updated,
    "already_preorder": already_preorder,
    "skipped": skipped,
}

print(f"Жалпы тексерілген тауар: {total}")
print(f"Стоктан предзаказға өзгертілген тауар: {updated}")
print(f"Бұрыннан предзаказдағы тауар: {already_preorder}")
print(f"Availability жоқ тауар: {skipped}")

# GitHub Actions workflow-на нақты сандарды беру.
github_output = os.environ.get("GITHUB_OUTPUT")
if github_output:
    with open(github_output, "a", encoding="utf-8") as f:
        for key, value in summary.items():
            f.write(f"{key}={value}\n")

print("Барлық тауар 1 күндік предзаказға тексерілді")
