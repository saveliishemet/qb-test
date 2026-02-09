import csv

INPUT_CSV = "BSGDATA_public_data_transfers.csv"
OUTPUT_CSV = "funding_transfers.csv"

# возвращает True если строка — трансфер по фандингу
def should_keep_row(row):
    type_exch = (row.get("type_exch")).strip()
    type_id_raw = row.get("type_id")
    type_id = str(type_id_raw).strip() if type_id_raw is not None else ""
    if type_exch.upper() == "FUNDING":
        return True
    if type_id == "405":
        return True
    return False

# читает data_transfers CSV, оставляет только строки по фандингу, записывает их в OUTPUT_CSV.
def main():
    with open(INPUT_CSV, "r", encoding="utf-8", newline="") as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            count = 0
            for row in reader:
                if should_keep_row(row):
                    writer.writerow(row)
                    count += 1
    print(f"Wrote {count} matching rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
