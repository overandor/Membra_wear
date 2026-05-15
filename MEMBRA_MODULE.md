# MEMBRA Module Contract — Wear

## Role

Wearable media-kit layer for MEMBRA. Turns eligible shirts, hoodies, jackets, bags, badges, hats, and apparel surfaces into QR/NFC campaign inventory.

## System inputs

- owner wearable asset records
- campaign IDs
- QR/NFC artifact IDs
- creative/package requirements
- proof photo requirements
- vendor package references

## System outputs

- wearable kit drafts
- QR/NFC wearable placement records
- vendor-ready package specs
- proof requirements
- owner campaign participation states

## Health

```text
GET /api/health
```

## Replit role

`service`

Runs as the wearable ad kit builder behind MEMBRA KPI and the MEMBRA OS website.

## Production boundary

Wearable campaigns require owner consent, creative approval, proof package, and review. No guaranteed earnings.
