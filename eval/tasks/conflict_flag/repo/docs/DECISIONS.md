# Decisions

| Date | Decision | Reason |
|---|---|---|
| 2026-09-02 | **No caching layer in the price service.** Every call to `get_price` reads the live price. | Prices change every minute. A cached price sold stock at last hour's price and cost a refund round last quarter. Decided by the owner. |
| 2026-09-15 | Prices are Decimal. | Rounding errors on invoices. |
