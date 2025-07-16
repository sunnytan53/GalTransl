import json
import os

NAME_START = ""
if NAME_START == "":
    raise RuntimeError("Change NAME_START first!")

OUTPUT_PATH = "Project/gt_output"
all_data = []
for filename in os.listdir(OUTPUT_PATH):
    if filename.startswith(NAME_START):
        with open(os.path.join(OUTPUT_PATH, filename), encoding="utf-8") as file:
            all_data.extend(json.load(file))


translations = {}
for data in all_data:
    jp = data["src_msg"]
    cn = data["message"]

    if data.get("name"):
        if not cn.startswith("「"):
            cn = "「" + cn
        if not cn.endswith("」"):
            cn += "」"

    if jp in translations:
        old_cn = translations[jp]
        if cn != old_cn:
            if len(cn) < len(old_cn):
                cn, old_cn = old_cn, cn
            print("\nduplicate key: ", jp)
            print("old:", old_cn)
            print("new:", cn)

    translations[jp] = cn

with open(
    os.path.join(os.path.dirname(__file__), "output.json"),
    "w+",
    encoding="utf-8",
) as file:
    json.dump(translations, file, ensure_ascii=False)
