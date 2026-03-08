# ============================================================
#  product_catalog.py
#  E-Commerce Product Catalog System
#  Uses: nested dicts, defaultdict, dict comprehensions, .get()
# ============================================================

from collections import defaultdict
from typing import Optional


# ─────────────────────────────────────────────────────────────
#  CATALOG  — 15 products across 4 categories
# ─────────────────────────────────────────────────────────────

catalog: dict = {
    # Electronics (4)
    "SKU001": {"name": "Laptop Pro",      "price": 75000, "category": "electronics", "stock": 15, "rating": 4.7, "tags": ["computer", "work", "portable"]},
    "SKU002": {"name": "Smartphone X",    "price": 45000, "category": "electronics", "stock": 8,  "rating": 4.5, "tags": ["phone", "portable", "camera"]},
    "SKU003": {"name": "Wireless Earbuds","price":  3500, "category": "electronics", "stock": 0,  "rating": 4.2, "tags": ["audio", "portable", "wireless"]},
    "SKU004": {"name": "Smart Watch",     "price": 12000, "category": "electronics", "stock": 5,  "rating": 4.0, "tags": ["wearable", "fitness", "portable"]},

    # Clothing (4)
    "SKU005": {"name": "Denim Jacket",    "price":  2500, "category": "clothing",    "stock": 20, "rating": 4.1, "tags": ["casual", "outerwear", "unisex"]},
    "SKU006": {"name": "Running Shoes",   "price":  4000, "category": "clothing",    "stock": 12, "rating": 4.3, "tags": ["fitness", "footwear", "sport"]},
    "SKU007": {"name": "Casual T-Shirt",  "price":   800, "category": "clothing",    "stock": 50, "rating": 3.9, "tags": ["casual", "everyday", "unisex"]},
    "SKU008": {"name": "Formal Trousers", "price":  1800, "category": "clothing",    "stock": 0,  "rating": 3.7, "tags": ["formal", "office", "work"]},

    # Books (4)
    "SKU009": {"name": "Clean Code",           "price":  650, "category": "books", "stock": 30, "rating": 4.8, "tags": ["programming", "best-seller", "work"]},
    "SKU010": {"name": "Python Crash Course",  "price":  550, "category": "books", "stock": 25, "rating": 4.6, "tags": ["programming", "beginner", "computer"]},
    "SKU011": {"name": "Atomic Habits",        "price":  499, "category": "books", "stock": 40, "rating": 4.7, "tags": ["self-help", "best-seller", "productivity"]},
    "SKU012": {"name": "Deep Work",            "price":  420, "category": "books", "stock": 0,  "rating": 4.5, "tags": ["self-help", "productivity", "work"]},

    # Food (3)
    "SKU013": {"name": "Organic Oats",         "price":  350, "category": "food", "stock": 100, "rating": 4.4, "tags": ["organic", "breakfast", "healthy"]},
    "SKU014": {"name": "Dark Chocolate Bar",   "price":  180, "category": "food", "stock": 200, "rating": 4.6, "tags": ["snack", "organic", "best-seller"]},
    "SKU015": {"name": "Green Tea (50 bags)",  "price":  220, "category": "food", "stock": 75,  "rating": 4.3, "tags": ["beverage", "healthy", "organic"]},
}


# ─────────────────────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────────────────────

def _safe_get(sku: str, key: str, default=None):
    """Return product[key] safely; returns default if sku or key missing."""
    return catalog.get(sku, {}).get(key, default)


# ─────────────────────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────────────────────

def search_by_tag(tag: str) -> dict[str, list[str]]:
    """
    Return all products containing the given tag, grouped by tag.
    Uses defaultdict to collect SKUs under each tag.

    Args:
        tag: The tag string to search for.

    Returns:
        A dict mapping the tag to a list of matching SKU strings.
        Empty dict if no products have that tag.

    Example:
        >>> search_by_tag('portable')
        {'portable': ['SKU001', 'SKU002', 'SKU003', 'SKU004']}
    """
    tag_index: defaultdict = defaultdict(list)
    for sku, product in catalog.items():
        for t in product.get("tags", []):
            tag_index[t].append(sku)

    return {tag: tag_index[tag]} if tag in tag_index else {}


def out_of_stock() -> dict[str, dict]:
    """
    Return all products where stock == 0.
    Uses dict comprehension with .get() for safe access.

    Returns:
        Dict of {sku: product_dict} for zero-stock products.
    """
    return {
        sku: product
        for sku, product in catalog.items()
        if product.get("stock", 1) == 0
    }


def price_range(min_price: float, max_price: float) -> dict[str, dict]:
    """
    Filter products whose price falls within [min_price, max_price].

    Args:
        min_price: Minimum price (inclusive).
        max_price: Maximum price (inclusive).

    Returns:
        Dict of matching {sku: product_dict}.
    """
    return {
        sku: product
        for sku, product in catalog.items()
        if min_price <= product.get("price", 0) <= max_price
    }


def category_summary() -> dict[str, dict]:
    """
    For each category compute: count, avg_price, avg_rating.
    Uses defaultdict(list) to accumulate values before computing averages.

    Returns:
        Dict mapping category name to {'count', 'avg_price', 'avg_rating'}.

    Example:
        >>> category_summary()
        {'electronics': {'count': 4, 'avg_price': 33875.0, 'avg_rating': 4.35}, ...}
    """
    prices:  defaultdict = defaultdict(list)
    ratings: defaultdict = defaultdict(list)

    for product in catalog.values():
        cat = product.get("category", "unknown")
        prices[cat].append(product.get("price", 0))
        ratings[cat].append(product.get("rating", 0))

    return {
        cat: {
            "count":      len(prices[cat]),
            "avg_price":  round(sum(prices[cat])  / len(prices[cat]),  2),
            "avg_rating": round(sum(ratings[cat]) / len(ratings[cat]), 2),
        }
        for cat in prices
    }


def apply_discount(category: str, percent: float) -> dict[str, dict]:
    """
    Return a new catalog copy with prices reduced by percent for the given category.
    Does NOT mutate the original catalog.

    Args:
        category: Category name to discount (case-sensitive).
        percent:  Discount percentage, e.g. 10 means 10% off.

    Returns:
        Full catalog dict with discounted prices for the chosen category.
    """
    multiplier = 1 - (percent / 100)
    return {
        sku: {
            **product,
            "price": round(product.get("price", 0) * multiplier, 2)
            if product.get("category") == category
            else product.get("price", 0)
        }
        for sku, product in catalog.items()
    }


def merge_catalogs(catalog1: dict, catalog2: dict) -> dict:
    """
    Merge two product catalogs.
    If the same SKU exists in both, catalog2 values take precedence
    (newer catalog wins), but stock quantities are summed.

    Args:
        catalog1: Base catalog dict.
        catalog2: Incoming catalog dict.

    Returns:
        Merged catalog dict.
    """
    merged = {**catalog1}   # start with catalog1 (equivalent to catalog1 | catalog2)

    for sku, product in catalog2.items():
        if sku in merged:
            # Merge: keep catalog2 data, but add stock from both
            combined_stock = merged[sku].get("stock", 0) + product.get("stock", 0)
            merged[sku] = {**merged[sku], **product, "stock": combined_stock}
        else:
            merged[sku] = product

    return merged


# ─────────────────────────────────────────────────────────────
#  DEMO / MAIN
# ─────────────────────────────────────────────────────────────

def divider(title: str) -> None:
    print(f"\n{'─' * 60}\n  {title}\n{'─' * 60}")


def main() -> None:
    divider("📦 FULL CATALOG")
    for sku, p in catalog.items():
        print(f"  {sku}  {p['name']:<25} ₹{p['price']:>7,}  "
              f"stock={p['stock']:>3}  ⭐{p['rating']}  [{p['category']}]")

    divider("🏷️  SEARCH BY TAG: 'portable'")
    result = search_by_tag("portable")
    for tag, skus in result.items():
        print(f"  {tag}: {skus}")

    divider("❌ OUT OF STOCK")
    for sku, p in out_of_stock().items():
        print(f"  {sku}: {p['name']}")

    divider("💰 PRICE RANGE ₹400 – ₹5,000")
    for sku, p in price_range(400, 5000).items():
        print(f"  {sku}: {p['name']:<25} ₹{p['price']:,}")

    divider("📊 CATEGORY SUMMARY")
    for cat, stats in category_summary().items():
        print(f"  {cat:<12}  count={stats['count']}  "
              f"avg_price=₹{stats['avg_price']:,.2f}  "
              f"avg_rating={stats['avg_rating']}")

    divider("🎁 APPLY 15% DISCOUNT TO ELECTRONICS")
    discounted = apply_discount("electronics", 15)
    for sku, p in discounted.items():
        if p["category"] == "electronics":
            original = catalog[sku]["price"]
            print(f"  {p['name']:<20}  ₹{original:,} → ₹{p['price']:,}")

    divider("🔀 MERGE CATALOGS")
    extra_catalog = {
        "SKU001": {"name": "Laptop Pro", "price": 70000, "category": "electronics",
                   "stock": 5, "rating": 4.8, "tags": ["computer", "work"]},   # dup SKU
        "SKU016": {"name": "Yoga Mat",   "price": 1500,  "category": "fitness",
                   "stock": 30, "rating": 4.2, "tags": ["fitness", "sport"]},  # new
    }
    merged = merge_catalogs(catalog, extra_catalog)
    print(f"  Original catalog size : {len(catalog)}")
    print(f"  Merged  catalog size  : {len(merged)}")
    print(f"  SKU001 stock after merge (15+5=20): {merged['SKU001']['stock']}")
    print(f"  SKU001 price after merge (catalog2 wins): ₹{merged['SKU001']['price']:,}")

    print()


if __name__ == "__main__":
    main()
