import csv
from datetime import datetime
from pathlib import Path

INPUT_CSV = "task 2.csv"
OUTPUT_CSV = "pl_by_instrument.csv"

def parse_ts(ts): # конвертация string в дэйттайм который можно сортировать
    parts = ts.strip().split()
    d = [int(x) for x in parts[0].split("/")]
    t = [int(x) for x in parts[1].split(":")]
    year = 2000 + d[2]
    return datetime(year, d[0], d[1], t[0], t[1])


def run(input_path=None, output_path=None):
    input_path = INPUT_CSV
    output_path = OUTPUT_CSV

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda x: parse_ts(x["ts"].strip())) # сортировка датасета по времени

    by_instrument = {} # открываем словарь в котором будут жить все позиции
    for r in rows:
        instrument = r["instrument_exch"]
        amount = float(r["amount"])
        price = float(r["price"])
        side = int(float(r["side"]))
        if instrument not in by_instrument:
            by_instrument[instrument] = {"lots": [], "short_lots": [], "realized_quote": 0.0, "quote_ccy": r["cur_quote"], "last_price": price}
        existing_position = by_instrument[instrument]
        existing_position["last_price"] = price
        if side == 1: # если получаем заявку на покупку - смотрим есть ли у нас шорт лоты. если есть - удаляем их до тех пор пока или они не закончатся или заявка не закончится. если лоты закончились раньше - пишем остаток в лонг
            remaining = amount
            while remaining > 0 and existing_position["short_lots"]:
                lot_amount, lot_price = existing_position["short_lots"][0] # самыми первыми уходят самые старые лоты
                close_amount = min(remaining, lot_amount) # чтобы не превысить случайно размер лота
                existing_position["realized_quote"] += close_amount * (lot_price - price)
                remaining -= close_amount
                if close_amount == lot_amount: # если остаток от позиции >= лота - мы удаляем лот, если нет - уменьшаем его на величину позиции
                    existing_position["short_lots"].pop(0)
                else:
                    existing_position["short_lots"][0] = (lot_amount - close_amount, lot_price)
            if remaining > 0:
                existing_position["lots"].append((remaining, price))
        else: # совершенно аналогичная логика в случае если видим заявку на продажу, только убираем теперь лонг лоты, очевидно
            remaining = amount
            while remaining > 0 and existing_position["lots"]:
                lot_amount, lot_price = existing_position["lots"][0]
                close_amount = min(remaining, lot_amount)
                existing_position["realized_quote"] += close_amount * (price - lot_price)
                remaining -= close_amount
                if close_amount == lot_amount:
                    existing_position["lots"].pop(0)
                else:
                    existing_position["lots"][0] = (lot_amount - close_amount, lot_price)
            if remaining > 0:
                existing_position["short_lots"].append((remaining, price))

    results = []
    for instrument, existing_position in sorted(by_instrument.items()):
        quote = existing_position["quote_ccy"]
        last_price = existing_position["last_price"]
        realized_quote = existing_position["realized_quote"]
        lots, short_lots = existing_position["lots"], existing_position["short_lots"]
        unrealized_quote = 0.0
        if last_price:
            for amount, price in lots:
                unrealized_quote += amount * (last_price - price) # идем лот за лотом и считаем пнл как рост цены инструмента относительно цены покупки
            for amount, price in short_lots:
                unrealized_quote += amount * (price - last_price) # точно также считаем пнл, но уже как снижение цены, так как лот на продажу
        total_quote = realized_quote + unrealized_quote
        to_usd = (total_quote / last_price) if quote != "USD" else total_quote
        realized_usd = (realized_quote / last_price) if quote != "USD" else realized_quote
        unrealized_usd = (unrealized_quote / last_price) if quote != "USD" else unrealized_quote
        results.append({
            "instrument": instrument,
            "realized_pl_usd": round(realized_usd, 5),
            "unrealized_pl_usd": round(unrealized_usd, 5),
            "total_pl_usd": round(to_usd, 5),
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["instrument", "realized_pl_usd", "unrealized_pl_usd", "total_pl_usd"])
        w.writeheader()
        w.writerows(results)
    return results


if __name__ == "__main__":
    run()
