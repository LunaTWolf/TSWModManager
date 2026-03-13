import os
import shutil
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------

SAVE_FOLDER = "../Saved/SaveGames"
ORIGINAL_FILE = os.path.join(SAVE_FOLDER, "UGCLiveries_0.sav")
BACKUP_FOLDER = "Backups"
PREFIX_FILE = "Data/prefix.sav"
LIVERIES_FOLDER = "Liveries"
NEW_FILE = os.path.join(SAVE_FOLDER, "UGCLiveries_0.sav")

# Explicit suffix (placed at end of file)
SUFFIX = bytes.fromhex("4E 6F 6E 65 00 00 00 00 00")

# Ensure folders exist
os.makedirs(BACKUP_FOLDER, exist_ok=True)
os.makedirs(SAVE_FOLDER, exist_ok=True)

# ----------------------------
# 1️⃣ Backup Original Save
# ----------------------------

if os.path.exists(ORIGINAL_FILE):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"UGCLiveries_0_{timestamp}.sav"
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)

    shutil.move(ORIGINAL_FILE, backup_path)

    print(f"Backup created: {backup_path}")

# ----------------------------
# 2️⃣ Start New Save From Prefix
# ----------------------------

if not os.path.exists(PREFIX_FILE):
    raise FileNotFoundError("Data/prefix.sav not found.")

with open(PREFIX_FILE, "rb") as f:
    new_save_data = f.read()

# ----------------------------
# 3️⃣ Append Valid .tsw6livery Files
# ----------------------------

if os.path.exists(LIVERIES_FOLDER):

    # Sort for consistency (important for stable rebuilds)
    for filename in sorted(os.listdir(LIVERIES_FOLDER)):

        # Skip temporary files
        if filename.startswith("livery_"):
            continue

        if filename.endswith(".tsw6livery"):

            file_path = os.path.join(LIVERIES_FOLDER, filename)

            with open(file_path, "rb") as f:
                new_save_data += f.read()

            print(f"Added: {filename}")

# ----------------------------
# 4️⃣ Add Suffix At End
# ----------------------------

new_save_data += SUFFIX

# ----------------------------
# 5️⃣ Write Final Save
# ----------------------------

with open(NEW_FILE, "wb") as f:
    f.write(new_save_data)

print("UGCLiveries_0.sav successfully rebuilt.")