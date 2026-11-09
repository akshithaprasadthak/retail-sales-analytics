import csv
import random
import sqlite3
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOT = datetime(2025, 3, 3, tzinfo=timezone.utc)

def records():
    rng = random.Random(42)
    start = date(2025, 1, 1)
    categories = {"Electronics": (13900, 0.15), "Home": (6100, 0.07),
                  "Apparel": (4900, 0.19), "Beauty": (3400, 0.05)}
    for i in range(1, 1201):
        day = start + timedelta(days=rng.randrange(181))
        category = rng.choice(list(categories))
        price, return_probability = categories[category]
        gross = price * rng.randint(1, 4) + rng.randint(-900, 900)
        refund = rng.choice([gross, gross // 2]) if rng.random() < return_probability else 0
        yield (i, day.isoformat(), rng.choice(["Online", "Store"]), category, gross, refund)

def display(key, value):
    if value is None:
        return "N/A"
    if key.endswith("_cents"):
        return f"${value / 100:,.2f}"
    if key.endswith("_pct"):
        return f"{value:.1f}%"
    return f"{value:,}" if isinstance(value, int) else str(value)

def label(key):
    return key.removesuffix("_cents").replace("_pct", " %").replace("_", " ").title()

def save_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)

def table(rows):
    columns = list(rows[0])
    header = "".join(f"<th scope='col'>{escape(label(key))}</th>" for key in columns)
    body = "".join("<tr>" + "".join(f"<td>{escape(display(key, row[key]))}</td>"
                   for key in columns) + "</tr>" for row in rows)
    return f"<div class='scroll'><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div>"

def chart(rows, group, measure):
    ceiling = 100 if measure.endswith("_pct") else max(row[measure] or 0 for row in rows)
    return "".join(
        f"<div class='bar-row'><span>{escape(row[group])}</span>"
        f"<div class='track'><i style='width:{(row[measure] or 0) * 100 / (ceiling or 1):.1f}%'></i></div>"
        f"<b>{escape(display(measure, row[measure]))}</b></div>" for row in rows
    )

def build():
    data = ROOT
    reports = ROOT
    with sqlite3.connect(":memory:") as db:
        db.row_factory = sqlite3.Row
        db.execute("CREATE TABLE records (order_id INTEGER PRIMARY KEY, day TEXT NOT NULL, channel TEXT NOT NULL, category TEXT NOT NULL, gross_cents INTEGER NOT NULL CHECK (gross_cents > 0), refund_cents INTEGER NOT NULL CHECK (refund_cents BETWEEN 0 AND gross_cents))")
        fields = [row[1] for row in db.execute("PRAGMA table_info(records)")]
        save_csv(data / "sample.csv", fields, records())
        with (data / "sample.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            assert next(reader) == fields
            placeholders = ",".join("?" for _ in fields)
            db.executemany(f"INSERT INTO records VALUES ({placeholders})",
                           ([value if value != "" else None for value in row] for row in reader))

        results = {}
        for query in sorted(ROOT.glob("*.sql")):
            cursor = db.execute(query.read_text(encoding="utf-8"))
            rows = [dict(row) for row in cursor]
            results[query.stem] = rows
            save_csv(reports / f"{query.stem}.csv", [col[0] for col in cursor.description],
                     (row.values() for row in rows))
        totals = results["kpis"][0]
        trend, breakdown, extra = results["trend"], results["breakdown"], results["channel"]
        assert totals["orders"] == 1200
        assert totals["gross_cents"] - totals["refund_cents"] == totals["net_cents"]
        for rows in (trend, breakdown, extra):
            assert sum(row["orders"] for row in rows) == totals["orders"]
            assert sum(row["net_cents"] for row in rows) == totals["net_cents"]
    leader = breakdown[0]
    highest_returns = max(breakdown, key=lambda row: row["refunded_orders_pct"])
    best_month = max(trend, key=lambda row: row["net_cents"])
    findings = [
        f"{leader['category']} led net sales at {display('net_cents', leader['net_cents'])}.",
        f"{highest_returns['category']} had the highest share of refunded orders "
        f"({highest_returns['refunded_orders_pct']}%). Review product-level returns before changing promotions.",
        f"{best_month['month']} had the highest net revenue in the sample.",
    ]
    cards = "".join(f"<div><span>{escape(label(k))}</span><strong>{escape(display(k, v))}</strong></div>"
                    for k, v in totals.items())
    insights = "".join(f"<li>{escape(item)}</li>" for item in findings)
    bars = chart(trend, "month", "net_cents")
    sections = table(breakdown) + "<h2>Channel</h2>" + table(extra)
    template = (ROOT / "dashboard.template.html").read_text(encoding="utf-8")
    content = template.replace("@CARDS@", cards).replace("@BARS@", bars)
    content = content.replace("@INSIGHTS@", insights).replace("@TABLES@", sections)
    (ROOT / "index.html").write_text(content, encoding="utf-8")
    lines = ["# Findings from the synthetic sample", "", *(f"- {item}" for item in findings)]
    (reports / "findings.md").write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    print(totals)
    print("Checks passed. Open index.html to view the dashboard.")

if __name__ == "__main__":
    build()
