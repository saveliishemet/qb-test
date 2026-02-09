import csv
import json

INPUT_CSV = "funding_transfers.csv"
OUTPUT_CSV = "funding_transfers_OM.csv"
INSTRUMENTS_CSV = "BSGDATA_public_statichange_instruments_v2.csv"

# загружает все инструменты из instruments_v2.csv и возвращает только те, которые asset_base=OM, contract_type=perpetual
# есть ещё контракт типа futures, но их количество для asset_base=OM равно нулю 
def load_om_perp_symbols():
    seen = set()
    with open(INSTRUMENTS_CSV, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("asset_base")).strip().upper() != "OM":
                continue
            if (row.get("contract_type")).strip().lower() != "perpetual":
                continue
            for col in ("instrument_exch", "instrument_bender"):
                val = (row.get(col)).strip()
                if val:
                    seen.add(val)
                    seen.add(normalize_symbol(val))
    return seen

# приводит к верхнему регистру и заменяет дефисы на подчёркивания (разные биржи могут писать имена одинаковых инструментов по-разному)
def normalize_symbol(s):
    if not s:
        return ""
    return s.strip().upper().replace("-", "_")

# возвращает True, если строка мэтчится с именем инструмента из instruments_v2.csv(asset_base=OM, contract_type=perpetual)
def is_om_instrument(s, om_perp_symbols):
    if not s or not isinstance(s, str):
        return False
    raw = s.strip()
    norm = normalize_symbol(raw)
    return raw in om_perp_symbols or norm in om_perp_symbols

# собирает идентификаторы инструментов из info и response
def get_instrument_candidates(info_val, response_val):
    candidates = []
    for val in (info_val, response_val):
        if not val or not isinstance(val, str):
            continue
        raw = val.strip()
        if not raw:
            continue
        if raw.startswith("{"):
            try:
                data = json.loads(raw)
                for key in ("symbol", "instrument_name", "instId"):
                    val = data.get(key)
                    if val and isinstance(val, str):
                        candidates.append(val.strip())
            except (json.JSONDecodeError, TypeError):
                pass
        else:
            candidates.append(raw)
    return candidates

# возвращает True, если инструмент строки вытянутый из info/response входит в список instruments_v2.csv(asset_base=OM, contract_type=perpetual)
def row_has_om(row, om_perp_symbols):
    info_val = row.get("info")
    response_val = row.get("response")
    for cand in get_instrument_candidates(info_val, response_val):
        if is_om_instrument(cand, om_perp_symbols):
            return True
    return False

# читает funding_transfers.csv, оставляет только строки asset_base=OM, contract_type=perpetual, записывает funding_transfers_OM.csv.
def main():
    om_perp_symbols = load_om_perp_symbols()
    print(f"Loaded {len(om_perp_symbols)} OM perpetual symbol forms from {INSTRUMENTS_CSV}")
    with open(INPUT_CSV, "r", encoding="utf-8", newline="") as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError("CSV has no header")
        with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            count = 0
            for row in reader:
                if row_has_om(row, om_perp_symbols):
                    writer.writerow(row)
                    count += 1
    print(f"Wrote {count} OM funding rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
