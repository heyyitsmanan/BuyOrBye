from collections import Counter
from typing import Dict, List, Optional

from .data import PRODUCT_CATALOG


def resolve_product(raw_input: str) -> Optional[Dict]:
    normalized = raw_input.lower()
    for product in PRODUCT_CATALOG:
        if any(alias in normalized for alias in product["aliases"]):
            return product
    return None


def dominant_category(products: List[Dict]) -> str:
    counts = Counter(product["category"] for product in products)
    return counts.most_common(1)[0][0]


def apply_category_filter(products: List[Dict], category_mode: str) -> List[Dict]:
    if category_mode == "auto":
        chosen_category = dominant_category(products)
        return [product for product in products if product["category"] == chosen_category]
    return [product for product in products if product["category"] == category_mode]


def round_score(value: float) -> float:
    return max(0.0, min(10.0, round(value, 1)))


def mode_class(mode: str) -> str:
    if mode == "budget":
        return "highlight-budget"
    if mode == "quality":
        return "highlight-quality"
    return "highlight-balanced"


def score_products(products: List[Dict], mode: str) -> List[Dict]:
    prices = [product["price"] for product in products]
    min_price = min(prices)
    max_price = max(prices)
    price_range = max(max_price - min_price, 1)

    scored = []
    for product in products:
        price_score = round_score(10 - ((product["price"] - min_price) / price_range) * 10)
        review_signal = min(product["review_count"] / 20000, 1)
        quality_score = round_score(
            product["quality_base"] * 0.75 + product["rating"] * 1.3 + review_signal * 0.8
        )
        value_score = round_score(price_score * 0.45 + quality_score * 0.55)

        overall_score = value_score
        if mode == "budget":
            overall_score = round_score(price_score * 0.65 + quality_score * 0.35)
        elif mode == "quality":
            overall_score = round_score(price_score * 0.2 + quality_score * 0.8)

        scored.append(
            {
                **product,
                "price_score": price_score,
                "quality_score": quality_score,
                "value_score": value_score,
                "overall_score": overall_score,
            }
        )

    return sorted(scored, key=lambda product: product["overall_score"], reverse=True)


def build_reason(product: Dict, mode: str) -> str:
    if mode == "budget":
        return (
            f"{product['name']} wins for price-sensitive buyers because it delivers "
            "the strongest low-cost score without collapsing on quality."
        )
    if mode == "quality":
        return (
            f"{product['name']} stays ahead because its quality metrics are strong enough "
            "to justify the price within this comparison set."
        )
    return (
        f"{product['name']} offers the best balance between what you pay and what you get, "
        "making it the strongest value choice in this lineup."
    )


def build_recommendations(products: List[Dict], mode: str) -> List[Dict]:
    best_budget = sorted(products, key=lambda product: product["price"])[0]
    best_quality = sorted(products, key=lambda product: product["quality_score"], reverse=True)[0]
    best_overall = products[0]

    return [
        {
            "label": "Top pick for your priority" if mode == "budget" else "Best overall value",
            "product_key": best_overall["key"],
            "score": f"{best_overall['overall_score']}/10",
            "tone_class": mode_class(mode),
            "reason": build_reason(best_overall, mode),
        },
        {
            "label": "Best for lowest price",
            "product_key": best_budget["key"],
            "score": f"${best_budget['price']}",
            "tone_class": "highlight-budget",
            "reason": (
                f"{best_budget['name']} is the cheapest option in this set while still "
                f"holding a quality score of {best_budget['quality_score']}/10."
            ),
        },
        {
            "label": "Best for quality",
            "product_key": best_quality["key"],
            "score": f"{best_quality['quality_score']}/10",
            "tone_class": "highlight-quality",
            "reason": (
                f"{best_quality['name']} leads on quality thanks to stronger review "
                "sentiment, product maturity, and premium feature signals."
            ),
        },
    ]


def build_metrics(products: List[Dict]) -> List[Dict]:
    average_price = round(sum(product["price"] for product in products) / len(products))
    best_value = sorted(products, key=lambda product: product["value_score"], reverse=True)[0]
    quality_leader = sorted(products, key=lambda product: product["quality_score"], reverse=True)[0]

    return [
        {
            "label": "Average price",
            "value": f"${average_price}",
            "note": f"Across {len(products)} comparable products in the selected category.",
        },
        {
            "label": "Best value",
            "value": best_value["name"],
            "note": f"{best_value['value_score']}/10 value score based on price-to-quality balance.",
        },
        {
            "label": "Quality leader",
            "value": quality_leader["name"],
            "note": (
                f"{quality_leader['quality_score']}/10 quality score from ratings, reviews, "
                "and product signals."
            ),
        },
    ]


def compare_products(raw_entries: List[str], priority_mode: str, category_mode: str) -> Dict:
    cleaned_entries = [entry.strip() for entry in raw_entries if entry and entry.strip()]
    if len(cleaned_entries) < 2:
        return {
            "status_message": "Add at least two product links or known product keywords to compare.",
            "metrics": [],
            "recommendations": [],
            "products": [],
            "error": "too_few_products",
        }

    matched_products = [resolve_product(entry) for entry in cleaned_entries]
    matched_products = [product for product in matched_products if product]

    if len(matched_products) < 2:
        return {
            "status_message": (
                "This MVP recognizes seeded sample products only right now. "
                "Try the sample buttons to see the full comparison flow."
            ),
            "metrics": [],
            "recommendations": [],
            "products": [],
            "error": "unknown_products",
        }

    filtered_products = apply_category_filter(matched_products, category_mode)
    if len(filtered_products) < 2:
        return {
            "status_message": (
                "The chosen category filter removed too many items. "
                "Try Auto-detect or load one sample set."
            ),
            "metrics": [],
            "recommendations": [],
            "products": [],
            "error": "category_mismatch",
        }

    scored_products = score_products(filtered_products, priority_mode)
    return {
        "status_message": (
            "Comparison ready. Scores are normalized within this product set, "
            "so value is relative to the products currently on screen."
        ),
        "metrics": build_metrics(scored_products),
        "recommendations": build_recommendations(scored_products, priority_mode),
        "products": scored_products,
        "error": None,
    }
