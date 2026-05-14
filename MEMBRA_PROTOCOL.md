# MEMBRA Protocol

Membra_api is the system of record.

This repo follows the shared Membra protocol for wearable media inventory, garment templates, QR placement, NFC garment templates, wearable proof rules, and asset certification.

Core rule: a wearable is not campaign-ready until the owner, asset, creative, QR/NFC identity, and proof requirements are verified.

Shared IDs: own_, adv_, ast_, wear_, cmp_, crt_, plc_, kit_, qr_, nfc_, proof_, aud_.

Wearable states used here: draft, submitted, under_review, verified, rejected, paused, retired.

Wear kit states used here: planned, generated, ordered, shipped, delivered, confirmed_received, installed, active, expired, lost, damaged.

Wear proof should confirm garment identity, visible creative, time window, campaign zone, and owner consent.
