# Power BI Dashboard

This folder holds the Power BI report for the Tehran Real Estate project.

## Connect to PostgreSQL

1. Start the stack: `make up` (or `./run.sh`)
2. Open **Power BI Desktop**
3. **Get Data** → **PostgreSQL database**
4. Server: `localhost:5432`
5. Database: `tehran_real_estate` (from `.env`)
6. Select view: `vw_listings_analytics`

## Suggested pages

| Page | Visual | Field |
|------|--------|-------|
| Overview | Bar chart | Average `price_per_sqm` by `address` |
| Rooms | Column chart | Count / avg price by `rooms` |
| Build year | Line chart | Avg `price_per_sqm` by `build_year` (mock data) |
| Top areas | Table | Top 10 `address` by avg `price_per_sqm` |

## Files

- `real_estate_dashboard.pbix` — save your report here (gitignored; export manually)
- `dashboard_preview.png` — screenshot for README

After building the dashboard, add a screenshot to this folder and link it from the main README.
