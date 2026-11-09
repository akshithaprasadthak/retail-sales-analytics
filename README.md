# Retail Sales & Returns Analytics

Which categories drive net revenue, and where do refunds erode it?

[Downloadable dashboard](index.html) · [Analysis findings](findings.md) · [Sample CSV](sample.csv)

## Sample results

**1,200 orders · $188,817.44 net revenue · 10.3% of orders refunded**

Compare net sales and refunded-order rates by product category and sales channel. Inspect [monthly trends](trend.csv) and the [category breakdown](breakdown.csv).

## Reproduce the analysis

Run `python build.py` with Python 3.11 or newer. Open `index.html` in your browser.
No packages, database service, or credentials are required. The build generates a fixed-seed sample,
loads it into SQLite, runs the included SQL queries, validates that totals reconcile across breakdowns,
and exports a self-contained dashboard and CSV reports.

For a public dashboard, enable GitHub Pages from the repository root. The generated `index.html`
is ready to serve as the landing page.

## Data and definitions

One row per order with a single product category. `gross_cents` is revenue before refunds, and `refund_cents` is the partial or full refund. Net revenue equals gross less refunds. Refunded-order rate is orders with any refund divided by total orders. Refunds are assigned to the original order month. Taxes, shipping, and product margins are outside the dataset.

The sample is synthetic and intended to demonstrate analysis methods. Findings describe the sample.
