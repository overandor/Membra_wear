# Membra Wear

Membra Wear is the wearable media-kit module for MEMBRA.

It defines how clothing, bags, patches, event badges, and other wearable surfaces can carry verified QR or NFC campaign media through the Membra control plane.

## One-line thesis

Turn wearable surfaces into trackable physical media inventory with approved creative, QR or NFC attribution, proof review, and campaign reporting.

## Product category

- Wearable media inventory
- QR and NFC apparel module
- Print-on-demand campaign kit layer
- Physical proof and analytics module

## Supported surfaces

- T-shirts
- Hoodies
- Jackets
- Hats
- Tote bags
- Backpacks
- Delivery bags
- QR patches
- NFC patches
- Event badges

## Relationship to other repos

`Membra_ads` is the campaign control plane.

`Membra_wear` is the wearable catalog and fulfillment module.

`membra-qr-gateway` is the dashboard and QR/NFC interface.

`Membra_wallet` handles payout boundaries and audit rules.

## Wearable media kit lifecycle

1. Campaign is created in Membra Ads.
2. Creative is approved.
3. Wearable placement is selected.
4. Membra generates QR or NFC identity.
5. Print-ready files are generated.
6. Vendor produces the item or files are exported for manual production.
7. Recipient confirms receipt.
8. Proof media is submitted.
9. Proof is reviewed.
10. Campaign reporting begins.

## Proof requirements

Minimum proof package:

- visible wearable item
- visible campaign creative
- visible QR or NFC marker when applicable
- receipt confirmation
- timestamp

Optional proof package:

- location proof
- event context
- recurring campaign proof
- scan or tap activity report

## Vendor strategy

Use adapter interfaces rather than hardcoding one vendor.

- Printify for product and order automation.
- Printful for catalog, mockup, file, and order workflows.
- Gelato for global fulfillment.
- Manual vendor workflow for local printers or event batches.

## Current stage

Product module scaffold. Next step: add catalog schema, vendor adapter interfaces, and media-kit templates.
