from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load dataset
# df = pd.read_csv('C:/Users/Pranjal/OneDrive/Desktop/diet-chart/INDB(Indian Nutrient Databank).csv')
df = pd.read_csv('Indian_Nutrient_Databank.csv')

# Convert relevant columns to numeric
numeric_columns = ['energy_kcal', 'carb_g', 'protein_g', 'fat_g', 'freesugar_g', 'fibre_g', 'sodium_mg', 'potassium_mg', 'cholesterol_mg']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Define non-vegetarian keywords
non_veg_keywords = ["chicken", "egg", "fish", "mutton", "meat", "pork", "beef", "prawn", "shrimp"]
easy_to_digest_non_veg = ["chicken", "egg", "fish"]  # Lean meats
# Function to classify meals
def classify_meal(food_name):
    food_lower = food_name.lower()

    breakfast_keywords = ["tea", "coffee", "bread", "idli", "dosa", "cereal", "oats", "pancake", "toast", "paratha", "poha", "upma", "egg", "fruit", "drink", "lassi", "milkshake", "flake", "uttapam"]
    lunch_keywords = ["rice", "dal", "sandwich", "chapati", "roti", "curry", "biryani", "khichdi", "sambar", "sabzi", "thali", "soup", "parantha", "poori", "pulao", "naan", "bhatura", "soyabean", "kadhi", "chana", "baked", "dum", "paneer", "salad", "raita", "dahi", "chutney"]
    dinner_keywords = ["soup", "pasta", "sandwich", "salad", "paneer", "chicken", "fish", "stir-fry", "dal", "roti", "sabzi", "rice", "dum", "kofta", "baked", "kheer", "tikka"]

    if any(word in food_lower for word in breakfast_keywords):
        return "breakfast"
    elif any(word in food_lower for word in lunch_keywords):
        return "lunch"
    elif any(word in food_lower for word in dinner_keywords):
        return "dinner"
    return None

# Function to get diet recommendations
def get_diet(age, health_condition, diet_preference):
    filtered_df = df.copy()

    # Apply health condition filters
    if health_condition == 'high_protein':
        filtered_df = filtered_df[filtered_df['protein_g'] > 15]
    elif health_condition == 'low_sugar':
        filtered_df = filtered_df[filtered_df['freesugar_g'] < 5]
    elif health_condition == 'hypertension':
        filtered_df = filtered_df[filtered_df['sodium_mg'] < 200]
    elif health_condition == 'kidney_disease':
        filtered_df = filtered_df[filtered_df['potassium_mg'] < 300]
    elif health_condition == 'diabetes':
        filtered_df = filtered_df[(filtered_df['carb_g'] < 50) & (filtered_df['fibre_g'] > 5)]
    elif health_condition == 'obesity':
        filtered_df = filtered_df[(filtered_df['fat_g'] < 10) & (filtered_df['energy_kcal'] < 500)]
    elif health_condition == 'heart_disease':
        filtered_df = filtered_df[(filtered_df['cholesterol_mg'] < 50) & (filtered_df['sfa_mg'] < 500)]

    # Restrict non-veg for users 50+
    # if age >= 50:
    #     filtered_df = filtered_df[~filtered_df['food_name'].str.contains('|'.join(non_veg_keywords), case=False, na=False)]
    if age >= 50:
        if diet_preference == 'non-vegetarian':
            filtered_df = filtered_df[filtered_df['food_name'].str.contains('|'.join(easy_to_digest_non_veg), case=False, na=False)]
        else:
            filtered_df = filtered_df[~filtered_df['food_name'].str.contains('|'.join(non_veg_keywords), case=False, na=False)]

    # Apply diet preference filter
    if diet_preference == 'vegetarian':
        filtered_df = filtered_df[~filtered_df['food_name'].str.contains('|'.join(non_veg_keywords), case=False, na=False)]
    elif diet_preference == 'non-vegetarian':
        filtered_df = filtered_df[filtered_df['food_name'].str.contains('|'.join(non_veg_keywords), case=False, na=False)]

    # Categorize meals
    breakfast_items = filtered_df[filtered_df['food_name'].apply(classify_meal) == "breakfast"]
    lunch_items = filtered_df[filtered_df['food_name'].apply(classify_meal) == "lunch"]
    dinner_items = filtered_df[filtered_df['food_name'].apply(classify_meal) == "dinner"]

    # Function to get exactly 3 items
    def get_sample(df_subset, n=3):
        if not df_subset.empty:
            return df_subset.sample(n=min(n, len(df_subset)), replace=False)['food_name'].tolist()
        return []

    # Assign meal items
    breakfast = get_sample(breakfast_items)
    lunch = get_sample(lunch_items)
    dinner = get_sample(dinner_items)

    # Fallback if empty
    if not breakfast:
        breakfast = get_sample(filtered_df, 3)
    if not lunch:
        lunch = get_sample(filtered_df, 3)
    if not dinner:
        dinner = get_sample(filtered_df, 3)

    # Return dictionary
    return {
        "Breakfast": breakfast,
        "Lunch": lunch,
        "Dinner": dinner
    }

@app.route("/", methods=["GET", "POST"])
def index():
    diet_chart = None

    if request.method == "POST":
        age = int(request.form['age'])
        health_condition = request.form['health_condition']
        diet_preference = request.form['diet_preference']
        diet_chart = get_diet(age, health_condition, diet_preference)

        return render_template("diet_chart.html", diet_chart=diet_chart)

    return render_template("index.html")

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) # Get port from environment or default to 5000
    app.run(host='0.0.0.0', port=port)



















# #  for classification of breakfast, lunch and dinner
# from flask import Flask, render_template, request,redirect,url_for
# import pandas as pd

# app = Flask(__name__)

# # Load dataset
# df = pd.read_csv('C:/Users/Pranjal/OneDrive/Desktop/diet-chart/INDB(Indian Nutrient Databank).csv')

# # Convert relevant columns to numeric
# numeric_columns = ['energy_kcal', 'carb_g', 'protein_g', 'fat_g', 'freesugar_g', 'fibre_g', 'sodium_mg', 'potassium_mg', 'cholesterol_mg']
# df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# # Food classification function
# def classify_meal(food_name):
#     food_lower = food_name.lower()
    
#     breakfast_keywords = ["tea", "coffee", "bread", "idli", "dosa", "cereal", "oats", "pancake", "toast", "paratha", "poha", "upma", "egg", "fruit", "drink", "lassi", "milkshake", "flake", "uttapam"]
#     lunch_keywords = ["rice", "dal", "sandwich", "chapati", "roti", "curry", "biryani", "khichdi", "sambar", "sabzi", "thali", "soup", "parantha", "poori", "pulao", "naan", "bhatura", "soyabean", "kadhi", "chana", "baked", "dum", "paneer", "salad", "raita", "dahi", "chutney"]
#     dinner_keywords = ["soup", "pasta", "sandwich", "salad", "paneer", "chicken", "fish", "stir-fry", "dal", "roti", "sabzi", "rice", "dum", "kofta", "baked", "kheer", "tikka"]
    
#     if any(word in food_lower for word in breakfast_keywords):
#         return "breakfast"
#     elif any(word in food_lower for word in lunch_keywords):
#         return "lunch"
#     elif any(word in food_lower for word in dinner_keywords):
#         return "dinner"
#     return None  # If the food does not fit any category

# #extra
# non_veg_keywords = ["chicken", "egg", "fish", "mutton", "meat", "pork", "beef", "prawn", "shrimp"]




# # Function to get diet recommendations
# def get_diet(age, health_condition, diet_preference):
#     filtered_df = df.copy()

#     # Apply health condition filters
#     if health_condition == 'high_protein':
#         filtered_df = filtered_df[filtered_df['protein_g'] > 15]
#     elif health_condition == 'low_sugar':
#         filtered_df = filtered_df[filtered_df['freesugar_g'] < 5]
#     elif health_condition == 'hypertension':
#         filtered_df = filtered_df[filtered_df['sodium_mg'] < 200]
#     elif health_condition == 'kidney_disease':
#         filtered_df = filtered_df[filtered_df['potassium_mg'] < 300]
#     elif health_condition == 'diabetes':
#         filtered_df = filtered_df[(filtered_df['carb_g'] < 50) & (filtered_df['fibre_g'] > 5)]
#     elif health_condition == 'obesity':
#         filtered_df = filtered_df[(filtered_df['fat_g'] < 10) & (filtered_df['energy_kcal'] < 500)]
#     elif health_condition == 'heart_disease':
#         filtered_df = filtered_df[(filtered_df['cholesterol_mg'] < 50) & (filtered_df['sfa_mg'] < 500)]

#     # Restrict non-veg for users 50+
#     if age >= 50:
#         filtered_df = filtered_df[filtered_df['cholesterol_mg'] == 0]


#  # Apply diet preference filter based on food name
#     if diet_preference == 'vegetarian':
#         filtered_df = filtered_df[~filtered_df['food_name'].str.contains('|'.join(non_veg_keywords), case=False, na=False)]
#     elif diet_preference == 'non-vegetarian':
#         filtered_df = filtered_df[filtered_df['food_name'].str.contains('|'.join(non_veg_keywords), case=False, na=False)]
    
#     # Categorize meals
#     breakfast_items = filtered_df[filtered_df['food_name'].apply(classify_meal) == "breakfast"]
#     lunch_items = filtered_df[filtered_df['food_name'].apply(classify_meal) == "lunch"]
#     dinner_items = filtered_df[filtered_df['food_name'].apply(classify_meal) == "dinner"]

#     # Function to get exactly 3 items
#     def get_sample(df_subset, n=3):
#         if not df_subset.empty:
#             return df_subset.sample(n=min(n, len(df_subset)), replace=False)['food_name'].tolist()
#         return []

#     # Assign meal items
#     breakfast = get_sample(breakfast_items)
#     lunch = get_sample(lunch_items)
#     dinner = get_sample(dinner_items)

#     # Fallback if empty
#     if not breakfast:
#         breakfast = get_sample(filtered_df, 3)
#     if not lunch:
#         lunch = get_sample(filtered_df, 3)
#     if not dinner:
#         dinner = get_sample(filtered_df, 3)

#     # Return dictionary
#     return {
#         "Breakfast": breakfast,
#         "Lunch": lunch,
#         "Dinner": dinner
#     }

# @app.route("/", methods=["GET", "POST"])
# def index():
#     diet_chart = None

#     if request.method == "POST":
#         age = int(request.form['age'])
#         health_condition = request.form['health_condition']
#         diet_preference = request.form['diet_preference']
#         diet_chart = get_diet(age, health_condition, diet_preference)

#     # return render_template("index.html", diet_chart=diet_chart)
#         return redirect(url_for('diet_chart', diet_chart=diet_chart))
#     return render_template("index.html")
# @app.route("/diet_chart")
# def diet_chart():
#     age = int(request.args.get('age', 0))
#     health_condition = request.args.get('health_condition', 'none')
#     diet_chart = get_diet(age, health_condition)
#     return render_template("diet_chart.html", diet_chart=diet_chart)


# if __name__ == "__main__":
#     app.run(debug=True)


