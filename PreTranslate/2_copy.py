import os
import json
import shutil

TRANSL_PATH = "Z/gtinput"
if os.path.exists(TRANSL_PATH):
    shutil.rmtree(TRANSL_PATH)
os.makedirs(TRANSL_PATH)

EXTRACTED_PATH = os.path.join(os.path.dirname(__file__), "Extracted")


# HARDCODED, varied for each VN
def name_is_update(path: str):
    _, tail = os.path.split(path)
    return tail.startswith("sppatch")


def process_each_json(filename: str, data: dict):
    # filter by filenames to only copy certain route
    if not filename.startswith("s_"):
        return None

    print("REMOVING:", data[0])
    assert "name" not in data[0]
    return data[1:] if len(data) >= 4 else []


# above HARDCODED


FILES = {}
for root, _, filenames in os.walk(EXTRACTED_PATH):
    for filename in filenames:
        if filename.endswith(".json"):
            if filename in FILES:
                HAS_DUPLICATE = True

                old_is_update = name_is_update(FILES[filename])
                new_is_update = name_is_update(root)

                if old_is_update or new_is_update:
                    print("\nDuplicate File:", filename)
                    print("Old Path:", os.path.relpath(FILES[filename], EXTRACTED_PATH))
                    print("New Path:", os.path.relpath(root, EXTRACTED_PATH))

                if old_is_update and not new_is_update:
                    print("Auto Behavior: using OLD path")
                elif new_is_update and not old_is_update:
                    FILES[filename] = root
                    print("Auto Behavior: using NEW path")
                else:
                    old_path = os.path.join(FILES[filename], filename)
                    new_path = os.path.join(root, filename)

                    print("1.", old_path := os.path.join(FILES[filename], filename))
                    print("2.", new_path := os.path.join(root, filename))

                    os.system(f"code --diff {old_path} {new_path}")

                    ans = ""
                    while ans not in ("1", "2"):
                        ans = input("Choose 1 or 2 for the final file to check")

                    if ans == "2":
                        FILES[filename] = root

            else:
                FILES[filename] = root


MIN_SIZE = 99999999
for filename, root in FILES.items():
    with open(os.path.join(root, filename), encoding="utf-8") as file:
        data = json.load(file)

    data = process_each_json(filename, data)

    if data is None:
        print(f"* Skipping {filename}")
        continue

    if len(data) < MIN_SIZE:
        MIN_SIZE = len(data)

    with open(os.path.join(TRANSL_PATH, filename), "w+", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

print("Min Size of scenes:", MIN_SIZE)
