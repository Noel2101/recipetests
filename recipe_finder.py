import requests
import os
from dotenv import load_dotenv

load_dotenv()

class RecipeFinder:
    def __init__(self):
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.base_url = "https://api.spoonacular.com/recipes"

    def search_recipes(self, ingredients):
        params = {
            "apiKey": self.api_key,
            "ingredients": ",".join(ingredients),
            "number": 5,
            "ranking": 2,
            "ignorePantry": True
        }

        try:
            response = requests.get(f"{self.base_url}/findByIngredients", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error accessing recipe API: {e}")
            return None

    def get_recipe_details(self, recipe_id):
        params = {
            "apiKey": self.api_key,
            "stepBreakdown": True
        }

        try:
            response = requests.get(f"{self.base_url}/{recipe_id}/information", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error accessing recipe API: {e}")
            return None

def main():
    print("🍳 Welcome to Fridge Recipe Finder! 🍳")
    print("\nWhat ingredients do you have? (separate with commas)")
    print("Example: chicken, rice, onion")
    
    ingredients = input("> ").split(",")
    ingredients = [i.strip() for i in ingredients]
    
    finder = RecipeFinder()
    results = finder.search_recipes(ingredients)
    
    if results:
        print(f"\nFound recipes that match your ingredients!")
        print("\nHere are the top 5 recipes (sorted by best ingredient match):")
        
        for i, recipe in enumerate(results, 1):
            print(f"\n{i}. {recipe['title']}")
            
            if recipe['usedIngredients']:
                print("   Using your ingredients:", 
                      ", ".join(ing['name'] for ing in recipe['usedIngredients']))
            
            if recipe['missedIngredients']:
                print("   You'll also need:", 
                      ", ".join(ing['name'] for ing in recipe['missedIngredients']))
                
            print(f"   Uses {recipe['usedIngredientCount']} of your ingredients")
            print(f"   Missing {recipe['missedIngredientCount']} ingredients")

        # Ask user which recipe they want to see
        print("\nEnter the number of the recipe you'd like to see instructions for (1-5):")
        try:
            choice = int(input("> ")) - 1
            if 0 <= choice < len(results):
                recipe_id = results[choice]['id']
                details = finder.get_recipe_details(recipe_id)
                
                if details:
                    print(f"\n=== {details['title']} ===")
                    print(f"Ready in: {details['readyInMinutes']} minutes")
                    print(f"Servings: {details['servings']}")
                    
                    print("\nInstructions:")
                    if details.get('instructions'):
                        steps = details.get('analyzedInstructions', [{}])[0].get('steps', [])
                        if steps:
                            for step in steps:
                                print(f"\n{step['number']}. {step['step']}")
                        else:
                            print(details['instructions'])
                    else:
                        print(f"Full recipe available at: {details['sourceUrl']}")
            else:
                print("Invalid recipe number!")
        except ValueError:
            print("Please enter a valid number!")
    else:
        print("\nNo recipes found with those ingredients. Try different combinations!")

if __name__ == "__main__":
    main()