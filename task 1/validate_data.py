import csv
import json
import sys

INPUT_CSV = "funding_transfers.csv"

REQUIRED_COLUMNS = ("account_id", "type_exch", "type_id", "side", "amount", "info", "response")
EXPECTED_TYPE_ID = "405"

def run_checks():
    errors = []
    with open(INPUT_CSV, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if not fieldnames:
            errors.append("CSV has no header")
            return errors
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            errors.append(f"Missing columns: {missing}")
            return errors

        for i, row in enumerate(reader, start=2):
            if not isinstance(row, dict):
                errors.append(f"Row {i}: row is not a dict")
                continue

            type_exch = (row.get("type_exch") or "").strip()
            type_id_raw = row.get("type_id")
            if type_id_raw is not None and not isinstance(type_id_raw, (str, int, float)):
                errors.append(f"Row {i}: type_id must be str/int/float, got {type(type_id_raw).__name__}")
            type_id = str(type_id_raw).strip() if type_id_raw not in (None, "") else ""
            is_funding_by_exch = type_exch and type_exch.upper() == "FUNDING"
            is_funding_by_id = type_id == EXPECTED_TYPE_ID
            if not is_funding_by_exch and not is_funding_by_id:
                errors.append(f"Row {i}: row must be funding (type_exch=FUNDING or type_id=405), got type_exch={type_exch!r}, type_id={type_id!r}")

            side_raw = row.get("side")
            if side_raw is not None and isinstance(side_raw, str) and side_raw.strip() != "":
                try:
                    side = int(side_raw)
                    if side not in (-1, 1):
                        errors.append(f"Row {i}: side must be -1 or 1, got {side}")
                except (ValueError, TypeError):
                    errors.append(f"Row {i}: side must be int -1 or 1, got {side_raw!r}")
            elif side_raw is not None and not isinstance(side_raw, str):
                errors.append(f"Row {i}: side must be str or None, got {type(side_raw).__name__}")

            amount_raw = row.get("amount")
            if amount_raw is not None and not isinstance(amount_raw, str):
                errors.append(f"Row {i}: amount must be str, got {type(amount_raw).__name__}")
            if amount_raw is not None and (amount_raw or "").strip():
                try:
                    float((amount_raw or "").strip())
                except (ValueError, TypeError):
                    errors.append(f"Row {i}: amount must be float-parsable, got {amount_raw!r}")

            for col in ("info", "response"):
                val = row.get(col)
                if val is not None and not isinstance(val, str):
                    errors.append(f"Row {i}: {col} must be str or None, got {type(val).__name__}")

            response_raw = (row.get("response") or "").strip()
            if response_raw and response_raw.startswith("{"):
                try:
                    data = json.loads(response_raw)
                    if not isinstance(data, dict):
                        errors.append(f"Row {i}: response JSON root must be dict")
                except (json.JSONDecodeError, TypeError) as e:
                    errors.append(f"Row {i}: response is not valid JSON: {e}")

            if len(errors) >= 50:
                errors.append("... (stopping after 50 issues)")
                break

    return errors

def main():
    try:
        errors = run_checks()
    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if errors:
        print("Validation failed. Issues:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"{INPUT_CSV} passed validation (formatting and consistency).")

if __name__ == "__main__":
    main()
