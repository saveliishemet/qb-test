import csv
import json
from collections import defaultdict

FUNDING_CSV = "funding_transfers_OM.csv"
ACCOUNTS_CSV = "accounts to exchanges.csv"
PNL_KEYS = ("pnl", "balChg", "realized_pnl", "transaction_cost", "income", "change", "funding")

# читает CSV аккаунтов и возвращает словарь: id аккаунта -> {exchange}
def load_account_to_exchange(path):
    out = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            a_id = (row.get("id")).strip()
            out[int(a_id)] = {"exchange": (row.get("exchange")).strip()}
    return out

# возвращает сумму и знак. в первую очередь проверяет пнл/аналоги, если таковых нет - использует amount * side для количества и side для знака
def get_row_amount_and_sign(row):
    # ищем пнл в response
    raw = (row.get("response")).strip()
    data = json.loads(raw)
    for key in PNL_KEYS:
        val = data.get(key)
        if val is None or val == "":
            continue
        try:
            v = float(val)
            if v != 0:
                return abs(v), -1 if v < 0 else 1
        except (TypeError, ValueError):
            pass
    # если пнл не найден в response мы строим его самостоятельно, используя эмаунт и сайд:
    v = float((row.get("amount")).strip())
    if v != 0:
        amt = abs(v)
        sign = int(row.get("side"))
        return (amt, sign) if sign is not None else (amt, None)
    return None, None

# читает funding_transfers_OM.csv, берет направление транзакции, группирует по бирже
def main():
    account_to_exchange = load_account_to_exchange(ACCOUNTS_CSV)
    by_exchange = defaultdict(lambda: {"paid": 0.0, "received": 0.0, "count_paid": 0, "count_received": 0, "skipped": 0})

    with open(FUNDING_CSV, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a_id = int((row.get("account_id")).strip())
            exchange = account_to_exchange.get(a_id)
            exchange_name = (exchange.get("exchange")).strip()

            amount, sign = get_row_amount_and_sign(row)
            if sign == -1:
                by_exchange[exchange_name]["paid"] += amount
                by_exchange[exchange_name]["count_paid"] += 1
            else:
                by_exchange[exchange_name]["received"] += amount
                by_exchange[exchange_name]["count_received"] += 1

    print("OM funding totals by exchange")
    total_paid = 0.0
    total_received = 0.0
    for exchange_name in sorted(by_exchange.keys()):
        st = by_exchange[exchange_name]
        total_paid += st["paid"]
        total_received += st["received"]
        net = st["received"] - st["paid"]
        print(f"\n  {exchange_name}")
        print(f"    Paid:     {st['paid']:>15.4f}  ({st['count_paid']} rows)")
        print(f"    Received: {st['received']:>15.4f}  ({st['count_received']} rows)")
        print(f"    Net:      {net:>15.4f}")
        if st["skipped"]:
            print(f"    Skipped:  {st['skipped']} rows (no amount or no sign)")
    print("\n")
    print(f"  TOTAL paid:     {total_paid:>15.4f}")
    print(f"  TOTAL received: {total_received:>15.4f}")
    print(f"  Net funding:    {total_received - total_paid:>15.4f}")
    print()

if __name__ == "__main__":
    main()
