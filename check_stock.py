"""Checks whether the GTA VI limited-edition vinyl is buyable and sends a
push notification through ntfy.sh if it is."""

import json
import os
import sys
import urllib.request

PRODUCT_URL = (
    "https://www.gtavi-thealbum.com/products/"
    "grand-theft-auto-vi-the-album-limited-edition-vinyl"
)
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

HEADERS = {"User-Agent": "Mozilla/5.0 (restock checker)"}


def notify(title: str, message: str) -> None:
    if not NTFY_TOPIC:
        sys.exit("NTFY_TOPIC secret is missing.")
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": "urgent",
            "Tags": "rotating_light",
            "Click": PRODUCT_URL,
        },
        method="POST",
    )
    urllib.request.urlopen(req, timeout=20)


def is_available() -> bool:
    # Shopify stores expose product data as JSON at <product-url>.js
    req = urllib.request.Request(PRODUCT_URL + ".js", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        product = json.load(resp)
    variants = product.get("variants", [])
    return bool(product.get("available")) or any(v.get("available") for v in variants)


def main() -> None:
    if TEST_MODE:
        notify("Test notification", "Your restock checker is set up correctly.")
        print("Test notification sent.")
        return

    if is_available():
        print("AVAILABLE - sending notification.")
        notify(
            "GTA VI vinyl is available!",
            "The limited-edition vinyl can be bought right now. Tap to open the store.",
        )
    else:
        print("Still sold out.")
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data="Checked just now: still sold out.".encode("utf-8"),
            headers={"Title": "Still sold out", "Priority": "min", "Tags": "hourglass"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=20)


if __name__ == "__main__":
    main()
