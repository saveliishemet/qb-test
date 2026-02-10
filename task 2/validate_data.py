import csv
from datetime import datetime
from pathlib import Path
 
INPUT_CSV = "task 2.csv"
OUTPUT_ISSUES_CSV = "data_consistency_issues.csv"
 
REQUIRED_COLUMNS = [
    "instrument_exch",
    "cur_base",
    "cur_quote",
    "side",
    "amount",
    "price",
    "ts",
]
 
 
# Same timestamp parsing expectations as find_PnL.py
def parse_ts(ts):
    parts = ts.strip().split()
    d = [int(x) for x in parts[0].split("/")]
    t = [int(x) for x in parts[1].split(":")]
    year = 2000 + d[2]
    return datetime(year, d[0], d[1], t[0], t[1])
 
 
def main():
    input_path = Path(__file__).parent / INPUT_CSV
    issues_path = Path(__file__).parent / OUTPUT_ISSUES_CSV
 
    issues = []
    instrument_info = {}
 
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
 
        if reader.fieldnames is None:
            raise SystemExit("CSV has no header row.")
 
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise SystemExit(f"Missing required columns: {missing}")
 
        for line_no, r in enumerate(reader, start=2):
            inst = (r.get("instrument_exch")).strip()
            base = (r.get("cur_base")).strip()
            quote = (r.get("cur_quote")).strip()
 
            if not inst:
                issues.append({"line": line_no, "instrument": "", "issue": "empty instrument_exch", "value": ""})
                continue
            if not base or not quote:
                issues.append({"line": line_no, "instrument": inst, "issue": "empty cur_base/cur_quote", "value": f"{base}/{quote}"})
 
            if inst not in instrument_info:
                instrument_info[inst] = {"base": base, "quote": quote, "first_line": line_no}
            else:
                if base and instrument_info[inst]["base"] and base != instrument_info[inst]["base"]:
                    issues.append({"line": line_no, "instrument": inst, "issue": "cur_base changed within instrument", "value": f"{instrument_info[inst]['base']} -> {base}"})
                if quote and instrument_info[inst]["quote"] and quote != instrument_info[inst]["quote"]:
                    issues.append({"line": line_no, "instrument": inst, "issue": "cur_quote changed within instrument", "value": f"{instrument_info[inst]['quote']} -> {quote}"})
 
            expected_inst = f"{base}/{quote}" if base and quote else ""
            if expected_inst and inst != expected_inst:
                issues.append({"line": line_no, "instrument": inst, "issue": "instrument_exch != cur_base/cur_quote", "value": expected_inst})
 
            try:
                parse_ts(r["ts"])
            except Exception as e:
                issues.append({"line": line_no, "instrument": inst, "issue": "bad ts (parse_ts failed)", "value": f"{r.get('ts')!r} ({e})"})
 
            try:
                side_raw = float(r["side"])
                side = int(side_raw)
                if side_raw not in (1.0, -1.0) or side not in (1, -1):
                    issues.append({"line": line_no, "instrument": inst, "issue": "side not in {1, -1}", "value": r.get("side")})
            except Exception as e:
                issues.append({"line": line_no, "instrument": inst, "issue": "bad side (float/int conversion failed)", "value": f"{r.get('side')!r} ({e})"})
 
            try:
                amount = float(r["amount"])
                if amount <= 0:
                    issues.append({"line": line_no, "instrument": inst, "issue": "amount must be > 0", "value": r.get("amount")})
            except Exception as e:
                issues.append({"line": line_no, "instrument": inst, "issue": "bad amount (float conversion failed)", "value": f"{r.get('amount')!r} ({e})"})
 
            try:
                price = float(r["price"])
                if price <= 0:
                    issues.append({"line": line_no, "instrument": inst, "issue": "price must be > 0", "value": r.get("price")})
            except Exception as e:
                issues.append({"line": line_no, "instrument": inst, "issue": "bad price (float conversion failed)", "value": f"{r.get('price')!r} ({e})"})
 
    for inst, info in instrument_info.items():
        base = info["base"]
        quote = info["quote"]
        if quote != "USD" and base != "USD":
            issues.append({
                "line": info["first_line"],
                "instrument": inst,
                "issue": "USD conversion may be invalid (base!=USD and quote!=USD)",
                "value": f"{base}/{quote}",
            })
 
    with open(issues_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["line", "instrument", "issue", "value"])
        w.writeheader()
        w.writerows(issues)
 
    print(f"Checked: {input_path}")
    print(f"Instruments: {len(instrument_info)}")
    print(f"Issues found: {len(issues)}")
    print(f"Issues CSV: {issues_path}")
 
    # Show a small preview in console
    for row in issues[:20]:
        print(f"line {row['line']}: {row['instrument']} - {row['issue']} ({row['value']})")
 
    if issues:
        raise SystemExit(1)
 
 
if __name__ == "__main__":
    main()
