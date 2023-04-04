import json

with open('ingredients.json') as f:
    data = json.load(f)

result = []
for i, ingredient in enumerate(data, start=1):
    """
    Форматирует данные из ingredients.json в формат, который
    принимает Django при загрузке фикстур.
    """
    result.append({
        "model": "recipes.ingredient",
        "pk": i,
        "fields": ingredient
    })

with open('ingredients_transformed.json', 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
