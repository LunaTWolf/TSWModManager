import os
import re
import zlib

INPUT_FILE = "../Saved/SaveGames/UGCLiveries_0.sav"
OUTPUT_FOLDER = "Liveries"
DATA_FOLDER = "Data"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# ----------------------------
# Clear Old Liveries
# ----------------------------

for filename in os.listdir(OUTPUT_FOLDER):
    if filename.endswith(".tsw6livery"):
        os.remove(os.path.join(OUTPUT_FOLDER, filename))

print("Old .tsw6livery files cleared.")

# ----------------------------
# Binary Patterns
# ----------------------------

START_BYTES = b"\x49\x44"

END_PATTERN = re.compile(
    b"\x4E\x6F\x6E\x65\x00.\x00\x00\x00"
)

ZLIB_START = b"\x78\x9C"
ZLIB_END = b"\x05\x00\x00\x00"

NAME_PATTERN = re.compile(
    b"\xFF\x01\x00\x00\x00.\x00\x00\x00"
)

NAME_TERMINATOR = b"\x00\x10\x00\x00\x00"

# ----------------------------
# Load File
# ----------------------------

with open(INPUT_FILE, "rb") as f:
    data = f.read()

start = 0
livery_index = 0

while True:
    start_index = data.find(START_BYTES, start)
    if start_index == -1:
        break

    match = END_PATTERN.search(data, start_index)

    if not match:
        start = start_index + 2
        continue

    end_index = match.end()

    livery_data = data[start_index:end_index]

    # ----------------------------
    # Skip Empty Livery Blocks
    # ----------------------------

    # An empty livery is extremely small
    # Adjust threshold if needed
    MIN_VALID_SIZE = 100  # safe starting point

    if len(livery_data) < MIN_VALID_SIZE:
        print("Skipped empty livery block.")
        start = end_index
        continue

    # ----------------------------
    # Save .tsw6livery (OVERWRITES)
    # ----------------------------

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"livery_{livery_index}.tsw6livery"
    )

    with open(output_path, "wb") as out:
        out.write(livery_data)

    # ----------------------------
    # Extract Zlib Section
    # ----------------------------

    z_start = livery_data.find(ZLIB_START)
    pretty_name = None

    if z_start != -1:
        z_end = livery_data.find(ZLIB_END, z_start)

        if z_end != -1:
            z_end += len(ZLIB_END)
            compressed = livery_data[z_start:z_end]

            try:
                decompressed = zlib.decompress(compressed)

                name_match = NAME_PATTERN.search(decompressed)

                if name_match:
                    name_start = name_match.end()
                    name_end = decompressed.find(
                        NAME_TERMINATOR,
                        name_start
                    )

                    if name_end != -1:
                        name_bytes = decompressed[name_start:name_end]
                        pretty_name = name_bytes.decode(
                            "utf-8",
                            errors="ignore"
                        ).strip()

            except Exception as e:
                print("Decompression failed:", e)

    # ----------------------------
    # Rename If Possible
    # ----------------------------

    if pretty_name:
        safe_name = "".join(
            c for c in pretty_name
            if c.isalnum() or c in (" ", "_", "-")
        ).strip()

        if safe_name:
            final_path = os.path.join(
                OUTPUT_FOLDER,
                f"{safe_name}.tsw6livery"
            )

            # Overwrite if exists
            if os.path.exists(final_path):
                os.remove(final_path)

            os.rename(output_path, final_path)
            print(f"Saved: {final_path}")
        else:
            print(f"Saved: {output_path}")
    else:
        print(f"Saved: {output_path}")

    livery_index += 1
    start = end_index

print("Extraction complete.")
