import requests
import json
import os

GEMINI_API_KEY = os.environ["AIzaSyARUZ2UuQqmjWZ0zNlb0YSXHyBNcY9ZUZM"]

# Get 1 product from OpenFoodFacts
def get_random_product():
    url = "https://world.openfoodfacts.org/api/v2/search?fields=product_name,ingredients_text,brands,code,categories_tags&page_size=1"
    res = requests.get(url)
    product = res.json()["products"][0]
    return product

# Use Gemini API to analyze product
def analyze_product(product):
    name = product.get("product_name", "")
    brand = product.get("brands", "")
    ingredients = product.get("ingredients_text", "")

    prompt = f"""
    Analyze the following product and return JSON with:
    - halal_status: whether it's halal or not (state "official", "likely halal", or "haram")
    - harmful_ingredients: list harmful ones if any
    - boycott_status: does the brand support genocide, child labor, unethical practices?

    Product: {name}
    Brand: {brand}
    Ingredients: {ingredients}

    Return JSON only, nothing else.
    """

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    res = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=data)
    response_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

    # Try to extract valid JSON (some formatting fixes)
    try:
        json_text = response_text.strip().strip("```json").strip("```")
        return json.loads(json_text)
    except Exception as e:
        print("❌ Failed to parse JSON:", response_text)
        return {}

# Save result
def save_result(data):
    with open("results.json", "a") as f:
        f.write(json.dumps(data) + "\n")

# Main
if __name__ == "__main__":
    product = get_random_product()
    analysis = analyze_product(product)
    result = {
        "name": product.get("product_name"),
        "brand": product.get("brands"),
        "barcode": product.get("code"),
        "category": product.get("categories_tags"),
        **analysis
    }
    save_result(result)
    print("✔ Done")
