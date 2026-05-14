"""MEMBRA Wear — wearable media-kit generator for Hugging Face/FastAPI.

Creates QR/NFC wearable placement manifests, vendor-ready kit packages,
proof requirements, CSV exports, and Stripe checkout links.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

import gradio as gr
import stripe
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

APP_NAME = "MEMBRA Wear"
DB_PATH = Path(os.getenv("DB_PATH", "/tmp/membra_wear.sqlite3"))
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:7860").rstrip("/")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
stripe.api_key = STRIPE_SECRET_KEY or None
api = FastAPI(title=APP_NAME)

class WearKitIn(BaseModel):
    owner_email: str
    campaign_name: str
    surface_type: str = Field(default="t-shirt")
    size_or_variant: str = "standard"
    destination_url: str
    vendor: str = "manual"
    geography: str = "local"
    creative_notes: str = ""
    proof_requirements: str = "visible wearable, visible campaign creative, visible QR/NFC marker, timestamp"

class CheckoutIn(BaseModel):
    email: str
    kit_id: str | None = None


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS wear_kits(
          kit_id TEXT PRIMARY KEY,
          owner_email TEXT,
          campaign_name TEXT,
          surface_type TEXT,
          size_or_variant TEXT,
          destination_url TEXT,
          vendor TEXT,
          geography TEXT,
          creative_notes TEXT,
          proof_requirements TEXT,
          qr_url TEXT,
          nfc_id TEXT,
          status TEXT,
          stripe_session_id TEXT,
          created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS proof_events(event_id TEXT PRIMARY KEY, kit_id TEXT, event_type TEXT, payload_json TEXT, created_at TEXT);
        """)

init_db()


def build_kit(data: WearKitIn) -> dict[str, Any]:
    kit_id = "wear_" + uuid.uuid4().hex[:12]
    qr_url = f"{APP_BASE_URL}/wear/{kit_id}"
    nfc_id = "nfc_" + uuid.uuid4().hex[:12]
    manifest = {
        "kit_id": kit_id,
        "status": "draft_pending_funding_and_production",
        "owner_email": data.owner_email,
        "campaign_name": data.campaign_name,
        "surface": {"type": data.surface_type, "variant": data.size_or_variant, "geography": data.geography},
        "identity": {"qr_url": qr_url, "nfc_id": nfc_id, "destination_url": data.destination_url},
        "vendor_package": {
            "vendor": data.vendor,
            "print_area": "front_or_patch",
            "file_policy": "export transparent PNG/SVG creative plus QR identity block",
            "manual_fallback": "local printer or event-batch production permitted with proof review",
        },
        "proof_policy": {"requirements": data.proof_requirements, "payout_rule": "No approved wearable proof means no payout eligibility."},
        "creative_notes": data.creative_notes,
        "created_at": now(),
    }
    with db() as conn:
        conn.execute("INSERT INTO wear_kits VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (kit_id, data.owner_email, data.campaign_name, data.surface_type, data.size_or_variant, data.destination_url, data.vendor, data.geography, data.creative_notes, data.proof_requirements, qr_url, nfc_id, manifest["status"], None, manifest["created_at"]))
    return manifest


def kit_rows() -> list[dict[str, Any]]:
    with db() as conn:
        rows = conn.execute("SELECT kit_id,campaign_name,owner_email,surface_type,size_or_variant,vendor,geography,status,qr_url,nfc_id,created_at FROM wear_kits ORDER BY created_at DESC LIMIT 200").fetchall()
    return [dict(r) for r in rows]


def export_kits() -> str:
    rows = kit_rows()
    path = "/tmp/membra_wear_kits.csv"
    if rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader(); writer.writerows(rows)
    else:
        Path(path).write_text("kit_id,campaign_name,status\n", encoding="utf-8")
    return path


def ui_create(owner_email, campaign_name, surface_type, size_variant, destination_url, vendor, geography, creative_notes, proof_requirements):
    try:
        manifest = build_kit(WearKitIn(owner_email=owner_email, campaign_name=campaign_name, surface_type=surface_type, size_or_variant=size_variant, destination_url=destination_url, vendor=vendor, geography=geography, creative_notes=creative_notes, proof_requirements=proof_requirements))
        return json.dumps(manifest, indent=2), kit_rows(), export_kits()
    except Exception as exc:
        return f"Error: {exc}", kit_rows(), None


def ui_checkout(email, kit_id):
    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        return "Stripe is not configured."
    session = stripe.checkout.Session.create(mode="payment", customer_email=email, line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}], success_url=f"{APP_BASE_URL}/?checkout=success", cancel_url=f"{APP_BASE_URL}/?checkout=cancelled", metadata={"kit_id": kit_id or ""})
    if kit_id:
        with db() as conn:
            conn.execute("UPDATE wear_kits SET stripe_session_id=?, status=? WHERE kit_id=?", (session.id, "funding_checkout_created", kit_id))
    return session.url

@api.get("/api/health")
def health():
    return {"ok": True, "app": APP_NAME, "stripe_configured": bool(STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET and STRIPE_PRICE_ID)}

@api.get("/api/kits")
def list_kits():
    return {"kits": kit_rows()}

@api.post("/api/kits")
def create_kit(data: WearKitIn):
    return build_kit(data)

@api.post("/api/stripe/create-checkout-session")
def checkout(data: CheckoutIn):
    return {"url": ui_checkout(data.email, data.kit_id or "")}

@api.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None)):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(500, "STRIPE_WEBHOOK_SECRET is not configured")
    body = await request.body()
    try:
        event = stripe.Webhook.construct_event(body, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(400, str(exc))
    obj = event["data"]["object"]
    kit_id = obj.get("metadata", {}).get("kit_id")
    if kit_id and event["type"] == "checkout.session.completed":
        with db() as conn:
            conn.execute("UPDATE wear_kits SET status=? WHERE kit_id=?", ("funded_pending_production", kit_id))
            conn.execute("INSERT INTO proof_events VALUES(?,?,?,?,?)", ("evt_" + uuid.uuid4().hex[:12], kit_id, event["type"], json.dumps(obj, default=str), now()))
    return JSONResponse({"received": True})

@api.get("/wear/{kit_id}")
def wear_scan(kit_id: str):
    with db() as conn:
        row = conn.execute("SELECT destination_url FROM wear_kits WHERE kit_id=?", (kit_id,)).fetchone()
        conn.execute("INSERT INTO proof_events VALUES(?,?,?,?,?)", ("evt_" + uuid.uuid4().hex[:12], kit_id, "scan", "{}", now()))
    if not row:
        raise HTTPException(404, "Wear kit not found")
    return PlainTextResponse(f"MEMBRA Wear scan recorded for {kit_id}. Destination: {row['destination_url']}")

with gr.Blocks(title=APP_NAME) as demo:
    gr.Markdown("# MEMBRA Wear\nWearable media-kit generator for QR/NFC apparel, bags, patches, and event badges.")
    with gr.Row():
        owner_email = gr.Textbox(label="Owner email")
        campaign_name = gr.Textbox(label="Campaign name")
    with gr.Row():
        surface_type = gr.Dropdown(["t-shirt", "hoodie", "jacket", "hat", "tote bag", "backpack", "delivery bag", "QR patch", "NFC patch", "event badge"], value="t-shirt", label="Surface")
        size_variant = gr.Textbox(label="Size / variant", value="standard")
        vendor = gr.Dropdown(["manual", "Printify", "Printful", "Gelato", "local vendor"], value="manual", label="Vendor")
    destination_url = gr.Textbox(label="Destination URL")
    geography = gr.Textbox(label="Geography", value="local")
    creative_notes = gr.Textbox(label="Creative notes", lines=3)
    proof_requirements = gr.Textbox(label="Proof requirements", value="visible wearable, visible campaign creative, visible QR/NFC marker, timestamp")
    create = gr.Button("Generate wearable kit", variant="primary")
    manifest = gr.Code(label="Wearable kit manifest", language="json")
    table = gr.Dataframe(label="Kit register", value=kit_rows, interactive=False)
    export = gr.File(label="CSV export")
    with gr.Row():
        checkout_email = gr.Textbox(label="Checkout email")
        checkout_kit = gr.Textbox(label="Kit ID")
    checkout_btn = gr.Button("Create Stripe checkout")
    checkout_url = gr.Textbox(label="Checkout URL")
    create.click(ui_create, [owner_email, campaign_name, surface_type, size_variant, destination_url, vendor, geography, creative_notes, proof_requirements], [manifest, table, export])
    checkout_btn.click(ui_checkout, [checkout_email, checkout_kit], [checkout_url])

app = gr.mount_gradio_app(api, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
