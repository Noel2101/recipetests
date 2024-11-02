import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class RecipeFinder:
    def __init__(self):
        self.api_key = st.secrets["SPOONACULAR_API_KEY"]
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
            st.error(f"Error accessing recipe API: {e}")
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
            st.error(f"Error accessing recipe API: {e}")
            return None

def main():
    st.title("🍳 Fridge Recipe Finder")
    st.write("Enter ingredients you have, and we'll find recipes for you!")

    # Get ingredients from user
    ingredients_input = st.text_input(
        "What ingredients do you have? (separate with commas)",
        placeholder="Example: chicken, rice, onion"
    )

    if ingredients_input:
        ingredients = [i.strip() for i in ingredients_input.split(",")]
        finder = RecipeFinder()
        results = finder.search_recipes(ingredients)

        if results:
            st.success("Found recipes that match your ingredients!")

            # Create tabs for each recipe
            tabs = st.tabs([recipe['title'] for recipe in results])

            for tab, recipe in zip(tabs, results):
                with tab:
                    # Show recipe details
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if recipe['usedIngredients']:
                            st.write("✅ Using your ingredients:",
                                ", ".join(ing['name'] for ing in recipe['usedIngredients']))
                        
                        if recipe['missedIngredients']:
                            st.write("🛒 You'll also need:",
                                ", ".join(ing['name'] for ing in recipe['missedIngredients']))

                    with col2:
                        st.write(f"Uses {recipe['usedIngredientCount']} of your ingredients")
                        st.write(f"Missing {recipe['missedIngredientCount']} ingredients")

                    # Get and show full recipe details
                    if st.button("Show Instructions", key=recipe['id']):
                        details = finder.get_recipe_details(recipe['id'])
                        if details:
                            st.write(f"⏱️ Ready in: {details['readyInMinutes']} minutes")
                            st.write(f"🍽️ Servings: {details['servings']}")
                            
                            st.subheader("Instructions:")
                            if details.get('instructions'):
                                steps = details.get('analyzedInstructions', [{}])[0].get('steps', [])
                                if steps:
                                    for step in steps:
                                        st.write(f"{step['number']}. {step['step']}")
                                else:
                                    st.write(details['instructions'])
                            else:
                                st.write(f"Full recipe available at: {details['sourceUrl']}")
        else:
            st.warning("No recipes found with those ingredients. Try different combinations!")

if __name__ == "__main__":
    main() 