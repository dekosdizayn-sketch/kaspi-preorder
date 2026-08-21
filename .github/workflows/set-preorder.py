import xml.etree.ElementTree as ET

INPUT_FILE = "ACTIVE_preorder1.xml"
OUTPUT_FILE = "ACTIVE_preorder1.xml"

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

changed = 0

for elem in root.iter():
    tag = elem.tag.split("}")[-1].lower().replace("-", "").replace("_", "")

    if "preorder" in tag and elem.text is not None:
        old = elem.text.strip()
        if old != "1":
            elem.text = "1"
            changed += 1

tree.write(
    OUTPUT_FILE,
    encoding="utf-8",
    xml_declaration=True
)

print(f"PREORDER 1 күнге өзгертілген өріс саны: {changed}")
