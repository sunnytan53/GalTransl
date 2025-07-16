import os
import shutil
import subprocess
import re

SOURCE = os.path.expanduser(r"~\Desktop\KrkrExtract_Output")
PROJECT_ROOT = os.path.dirname(__file__)

TOOL_PATH = os.path.join(PROJECT_ROOT, r"VNTextPatch\VNTextPatch.exe")
EXTRACTED_PATH = os.path.join(PROJECT_ROOT, "Extracted")

#
# currently galtransl use preference of sakura 7B
#

if os.path.exists(EXTRACTED_PATH):
    shutil.rmtree(EXTRACTED_PATH)
os.mkdir(EXTRACTED_PATH)


unsupported_extensions = tuple()
for src_root, _, filenames in os.walk(SOURCE):
    if filenames:
        os.mkdir(
            dst_root := os.path.join(EXTRACTED_PATH, os.path.relpath(src_root, SOURCE))
        )
        for filename in filenames:
            if filename.endswith(unsupported_extensions):
                continue

            res = subprocess.run(
                [
                    TOOL_PATH,
                    "extractlocal",
                    os.path.join(src_root, filename),
                    os.path.join(dst_root, filename) + ".json",
                ],
                capture_output=True,
            )
            if res.stdout:
                print(stdout := res.stdout.decode().strip())
                if stdout.startswith("Extension"):
                    exts = re.findall(r"\.\S*", stdout)
                    assert len(exts) == 1

                    extensions = set(unsupported_extensions)
                    extensions.add(exts[0])
                    unsupported_extensions = tuple(extensions)

            if res.stderr:
                print(res.stderr.decode())
                input("ERROR, hit enter to continue")


for src_root, _, filenames in os.walk(EXTRACTED_PATH):
    if not os.listdir(src_root):
        os.rmdir(src_root)
