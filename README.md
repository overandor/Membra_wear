# Membra Wear

**Membra Wear is the wearable QR/NFC media-kit module for MEMBRA Labs and the MEMBRA Proof Network.**

It turns shirts, hoodies, jackets, hats, tote bags, backpacks, delivery bags, patches, and event badges into verified physical media inventory.

## Company Context

- Company: **MEMBRA Labs**
- Flagship product: **MEMBRA Proof Network**
- Commercial wedge supported: **Membra Ads**
- Module: **Membra Wear**
- Category: wearable media kits, QR/NFC apparel, proof-backed campaign placements

## One-Line Thesis

Membra Wear turns wearable surfaces into trackable physical media inventory with approved creative, QR/NFC attribution, proof review, and campaign reporting.

## Product Role

Membra Wear extends the Membra Ads workflow into apparel and mobile physical surfaces.

It supports:

- campaign shirts
- hoodies and jackets
- hats
- tote bags
- backpacks
- delivery bags
- QR patches
- NFC patches
- event badges
- local promotional kits

## Wearable Media Kit Lifecycle

1. Campaign is created in Membra Ads.
2. Creative is approved.
3. Wearable placement is selected.
4. MEMBRA generates QR or NFC identity.
5. Print-ready files are generated.
6. Vendor produces the item or exports files for manual production.
7. Recipient confirms receipt.
8. Proof media is submitted.
9. Proof is reviewed.
10. Campaign reporting begins.

## Proof Requirements

Minimum proof package:

- visible wearable item
- visible campaign creative
- visible QR/NFC marker when applicable
- receipt confirmation
- timestamp

Optional proof package:

- location proof
- event context
- recurring campaign proof
- scan/tap activity report

## Vendor Strategy

Use adapter interfaces rather than hardcoding one vendor.

Potential rails:

- Printify for product and order automation
- Printful for catalog, mockup, file, and order workflows
- Gelato for global fulfillment
- local printers for event batches
- manual vendor workflow for high-touch campaigns

## Integration Points

| Repo | Relationship |
|---|---|
| `overandor/Membra_ads` | campaign, creative approval, media-kit request, proof rules |
| `overandor/Membra_vendor_adapters` | Printful/Printify/Gelato/local vendor ordering |
| `overandor/membra-qr-gateway` | wearable campaign status, scan/tap dashboard, proof view |
| `overandor/Membra_kpi` | wearable performance reports |
| `overandor/Membra_wallet` | reward eligibility and payout boundary |
| `overandor/Membra_proofbook` | proof hash and scan/tap ledger records |

## Safety Rules

- no payout eligibility without approved proof
- no campaign activation without approved creative
- no QR/NFC attribution without MEMBRA-controlled identifiers
- no guaranteed scan volume
- no guaranteed owner earnings
- no vendor order without explicit campaign state

## Productization Priority

Membra Wear is a strong commercial extension after Membra Ads and QR Gateway are demo-connected.

Next steps:

1. define wearable catalog schema
2. define media-kit object schema
3. define vendor adapter contract
4. create demo wearable campaign records
5. connect proof and scan states into QR Gateway

## Current Stage

Product module scaffold. Suitable for company packaging and demo roadmap; not yet a production vendor-integrated module.