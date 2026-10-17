"""Q2: Rank products extracted from saved HTML pages (standard library only).
Supported markup: product containers with class=product and name, price, rating
in class/id attributes or data-name/data-price/data-rating attributes.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

class ProductParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.products, self.current, self.capture, self.depth = [], None, None, 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").lower().split())
        if self.current is None and ("product" in classes or all(k in attrs for k in ("data-name", "data-price", "data-rating"))):
            self.current = {"name": attrs.get("data-name", ""), "price": attrs.get("data-price", ""), "rating": attrs.get("data-rating", "")}
            self.depth = 1
        elif self.current is not None:
            self.depth += 1
        if self.current is not None:
            for field in ("name", "price", "rating"):
                if not self.current[field] and (field in classes or field in attrs.get("id", "").lower()):
                    self.capture = field
                    break
    def handle_data(self, data):
        if self.current is not None and self.capture:
            self.current[self.capture] += data.strip()
    def handle_endtag(self, tag):
        if self.current is not None:
            self.depth -= 1
            if self.depth <= 0:
                if self.current.get("name"):
                    self.products.append(self.current)
                self.current = None
                self.depth = 0
        self.capture = None

def normalize_price(value):
    cleaned = re.sub(r"[^0-9.]", "", value.replace(",", ""))
    number = float(cleaned)
    if number < 0: raise ValueError("Price cannot be negative")
    return number

def read_products(path):
    parser = ProductParser()
    parser.feed(Path(path).read_text(encoding="utf-8", errors="replace"))
    for p in parser.products:
        try:
            name = " ".join(p["name"].split())
            rating = float(re.search(r"\d+(?:\.\d+)?", p["rating"]).group())
            price = normalize_price(p["price"])
            if name and 0 <= rating <= 5: yield {"name": name, "price": price, "rating": rating}
        except (ValueError, AttributeError):
            continue

def main():
    try:
        first = input("Number of pages and K: ").split()
        if len(first) != 2: raise ValueError("Enter p and k.")
        p, k = map(int, first)
        if not (1 <= p <= 5000 and 1 <= k <= 1000): raise ValueError("p or k is outside the allowed range.")
        paths = [input(f"HTML file {i + 1}: ").strip() for i in range(p)]
        best = {}
        for path in paths:
            for item in read_products(path):
                key = item["name"].casefold()
                old = best.get(key)
                if old is None or (item["rating"], -item["price"]) > (old["rating"], -old["price"]): best[key] = item
        ranked = sorted(best.values(), key=lambda x: (-x["rating"], x["price"], x["name"].casefold()))[:k]
        for item in ranked: print(f'{item["name"]} {item["price"]:g} {item["rating"]:g}')
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr); raise SystemExit(1)

if __name__ == "__main__": main()
