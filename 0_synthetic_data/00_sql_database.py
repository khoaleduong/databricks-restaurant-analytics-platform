import pandas as pd
import random
import os
from faker import Faker

fake = Faker(['en_GB'])  #  Great Britain (en_GB)

# ============================================
# RESTAURANTS - ENGLISH CITIES
# ============================================
def generate_restaurants():
    restaurants_data = [
        {
            "restaurant_id": "REST-LDN-001",
            "name": "The King's Arms Tavern",
            "city": "London",
            "country": "England",
            "address": "221 Baker Street, London",
            "opening_date": "2023-01-15",
            "phone": "+44-20-1234-5678"
        },
        {
            "restaurant_id": "REST-LDN-002",
            "name": "The British Bistro",
            "city": "London",
            "country": "England",
            "address": "Covent Garden, London",
            "opening_date": "2023-06-20",
            "phone": "+44-20-2345-6789"
        },
        {
            "restaurant_id": "REST-MAN-001",
            "name": "Manchester Chophouse",
            "city": "Manchester",
            "country": "England",
            "address": "Deansgate, Manchester",
            "opening_date": "2023-03-10",
            "phone": "+44-161-3456-7890"
        },
        {
            "restaurant_id": "REST-MAN-002",
            "name": "The Old Wellington Inn",
            "city": "Manchester",
            "country": "England",
            "address": "Cathedral Gates, Manchester",
            "opening_date": "2023-09-05",
            "phone": "+44-161-4567-8901"
        },
        {
            "restaurant_id": "REST-BIR-001",
            "name": "The Birmingham Balti House",
            "city": "Birmingham",
            "country": "England",
            "address": "Balti Triangle, Birmingham",
            "opening_date": "2024-02-14",
            "phone": "+44-121-5678-9012"
        },
        {
            "restaurant_id": "REST-LIV-001",
            "name": "The Liverpool Pantry",
            "city": "Liverpool",
            "country": "England",
            "address": "Albert Dock, Liverpool",
            "opening_date": "2023-11-20",
            "phone": "+44-151-6789-0123"
        },
        {
            "restaurant_id": "REST-LDS-001",
            "name": "Yorkshire Roast House",
            "city": "Leeds",
            "country": "England",
            "address": "Briggate, Leeds",
            "opening_date": "2023-07-18",
            "phone": "+44-113-7890-1234"
        },
        {
            "restaurant_id": "REST-BRS-001",
            "name": "The Bristol Cider House",
            "city": "Bristol",
            "country": "England",
            "address": "Harbourside, Bristol",
            "opening_date": "2024-01-30",
            "phone": "+44-117-8901-2345"
        },
        {
            "restaurant_id": "REST-NCL-001",
            "name": "Newcastle Ale House",
            "city": "Newcastle",
            "country": "England",
            "address": "Quayside, Newcastle upon Tyne",
            "opening_date": "2023-10-12",
            "phone": "+44-191-9012-3456"
        },
        {
            "restaurant_id": "REST-SHF-001",
            "name": "The Sheffield Pie Shop",
            "city": "Sheffield",
            "country": "England",
            "address": "Ecclesall Road, Sheffield",
            "opening_date": "2024-03-05",
            "phone": "+44-114-0123-4567"
        }
    ]

    df_restaurants = pd.DataFrame(restaurants_data)
    return df_restaurants

# ============================================
# MENU ITEMS - BRITISH CUISINE
# ============================================
def generate_menu_items():
    master_menu = [
        # Starters / Small Plates
        {"item_id": "ITEM-101", "name": "Yorkshire Pudding", "category": "Starter", "price": 5.50, "ingredients": "Flour, Eggs, Milk, Beef Dripping", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-102", "name": "Scotch Egg", "category": "Starter", "price": 6.50, "ingredients": "Hard-boiled Egg, Sausage Meat, Breadcrumbs", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-103", "name": "Prawn Cocktail", "category": "Starter", "price": 7.50, "ingredients": "Prawns, Marie Rose Sauce, Lettuce, Lemon", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-104", "name": "Cream of Mushroom Soup", "category": "Starter", "price": 5.00, "ingredients": "Mushrooms, Cream, Onions, Vegetable Stock", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-105", "name": "Whitebait", "category": "Starter", "price": 6.00, "ingredients": "Small Fish, Flour, Lemon, Tartare Sauce", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-106", "name": "Potted Shrimp", "category": "Starter", "price": 8.00, "ingredients": "Brown Shrimp, Butter, Nutmeg, Cayenne Pepper", "is_vegetarian": False, "spice_level": "Mild"},
        
        # Main Courses - Traditional British
        {"item_id": "ITEM-201", "name": "Fish and Chips", "category": "Main Course", "price": 15.00, "ingredients": "Cod or Haddock, Chips, Mushy Peas, Tartare Sauce", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-202", "name": "Roast Beef with Yorkshire Pudding", "category": "Main Course", "price": 18.00, "ingredients": "Beef Sirloin, Roast Potatoes, Vegetables, Gravy", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-203", "name": "Shepherd's Pie", "category": "Main Course", "price": 14.00, "ingredients": "Lamb Mince, Carrots, Peas, Mashed Potato, Gravy", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-204", "name": "Cottage Pie", "category": "Main Course", "price": 13.50, "ingredients": "Beef Mince, Carrots, Peas, Mashed Potato, Gravy", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-205", "name": "Toad in the Hole", "category": "Main Course", "price": 14.50, "ingredients": "Sausages, Yorkshire Pudding Batter, Onion Gravy", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-206", "name": "Bangers and Mash", "category": "Main Course", "price": 12.00, "ingredients": "Pork Sausages, Mashed Potato, Onion Gravy", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-207", "name": "Cornish Pasty", "category": "Main Course", "price": 10.00, "ingredients": "Beef, Potato, Swede, Onion, Shortcrust Pastry", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-208", "name": "Lancashire Hotpot", "category": "Main Course", "price": 14.00, "ingredients": "Lamb, Onions, Carrots, Potatoes", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-209", "name": "Beef Wellington", "category": "Main Course", "price": 28.00, "ingredients": "Beef Fillet, Pâté, Puff Pastry, Mushroom Duxelles", "is_vegetarian": False, "spice_level": "None"},
        
        # Vegetarian Options
        {"item_id": "ITEM-301", "name": "Vegetarian Roast", "category": "Main Course", "price": 14.00, "ingredients": "Nut Roast, Roast Vegetables, Gravy", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-302", "name": "Cauliflower Cheese", "category": "Main Course", "price": 11.00, "ingredients": "Cauliflower, Cheddar Cheese Sauce, Breadcrumbs", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-303", "name": "Mushroom Wellington", "category": "Main Course", "price": 15.00, "ingredients": "Mushrooms, Spinach, Puff Pastry", "is_vegetarian": True, "spice_level": "None"},
        
        # Sandwiches (British Classic)
        {"item_id": "ITEM-401", "name": "Ploughman's Sandwich", "category": "Sandwich", "price": 8.00, "ingredients": "Cheddar Cheese, Pickle, Lettuce, Tomato", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-402", "name": "Coronation Chicken Sandwich", "category": "Sandwich", "price": 9.00, "ingredients": "Chicken, Curry Mayonnaise, Apricot, Sultanas", "is_vegetarian": False, "spice_level": "Mild"},
        {"item_id": "ITEM-403", "name": "BLT Sandwich", "category": "Sandwich", "price": 8.50, "ingredients": "Bacon, Lettuce, Tomato, Mayonnaise", "is_vegetarian": False, "spice_level": "None"},
        
        # Puddings (Desserts)
        {"item_id": "ITEM-501", "name": "Sticky Toffee Pudding", "category": "Dessert", "price": 7.50, "ingredients": "Dates, Toffee Sauce, Vanilla Ice Cream", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-502", "name": "Apple Crumble", "category": "Dessert", "price": 6.50, "ingredients": "Apple, Oats, Flour, Sugar, Custard", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-503", "name": "Treacle Sponge Pudding", "category": "Dessert", "price": 7.00, "ingredients": "Sponge Cake, Golden Syrup, Custard", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-504", "name": "Bread and Butter Pudding", "category": "Dessert", "price": 6.00, "ingredients": "Bread, Butter, Raisins, Custard", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-505", "name": "Eton Mess", "category": "Dessert", "price": 6.50, "ingredients": "Strawberries, Meringue, Whipped Cream", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-506", "name": "Victoria Sponge Cake", "category": "Dessert", "price": 5.50, "ingredients": "Sponge Cake, Raspberry Jam, Whipped Cream", "is_vegetarian": True, "spice_level": "None"},
        
        # Scones (Afternoon Tea)
        {"item_id": "ITEM-601", "name": "Plain Scone", "category": "Bakery", "price": 3.00, "ingredients": "Flour, Butter, Milk, Baking Powder", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-602", "name": "Fruit Scone", "category": "Bakery", "price": 3.50, "ingredients": "Flour, Butter, Raisins, Milk", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-603", "name": "Cream Tea Set (Scone + Clotted Cream + Jam)", "category": "Afternoon Tea", "price": 7.00, "ingredients": "Scone, Clotted Cream, Strawberry Jam", "is_vegetarian": True, "spice_level": "None"},
        
        # Beverages (British Drinks)
        {"item_id": "ITEM-701", "name": "English Breakfast Tea", "category": "Beverage", "price": 3.00, "ingredients": "Black Tea, Milk, Sugar", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-702", "name": "Earl Grey Tea", "category": "Beverage", "price": 3.00, "ingredients": "Black Tea, Bergamot Oil", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-703", "name": "Pimm's Cup", "category": "Beverage", "price": 9.00, "ingredients": "Pimm's No. 1, Lemonade, Fruits, Mint", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-704", "name": "Real Ale (Pint)", "category": "Beverage", "price": 5.50, "ingredients": "Ale, Hops, Barley", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-705", "name": "Cider (Pint)", "category": "Beverage", "price": 5.00, "ingredients": "Apple Cider", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-706", "name": "Elderflower Cordial", "category": "Beverage", "price": 3.50, "ingredients": "Elderflower, Sugar, Water, Lemon", "is_vegetarian": True, "spice_level": "None"},
        {"item_id": "ITEM-707", "name": "Shandy", "category": "Beverage", "price": 4.00, "ingredients": "Lemonade, Beer", "is_vegetarian": True, "spice_level": "None"},
        
        # Full Breakfast Items (All-day)
        {"item_id": "ITEM-801", "name": "Full English Breakfast", "category": "All-Day", "price": 14.00, "ingredients": "Eggs, Bacon, Sausage, Beans, Tomato, Mushrooms, Toast", "is_vegetarian": False, "spice_level": "None"},
        {"item_id": "ITEM-802", "name": "Vegetarian Full Breakfast", "category": "All-Day", "price": 12.00, "ingredients": "Eggs, Veggie Sausage, Beans, Tomato, Mushrooms, Toast", "is_vegetarian": True, "spice_level": "None"}
    ]

    # Generate menu items for each restaurant
    menu_items_data = []
    restaurants_data = generate_restaurants().to_dict('records')

    for restaurant in restaurants_data:
        rest_id = restaurant["restaurant_id"]
        rest_city = restaurant["city"]
        
        for item in master_menu:
            # Price may vary by city (higher in London, lower in Northern cities)
            if rest_city == "London":
                price_multiplier = random.uniform(1.00, 1.15)
            elif rest_city in ["Manchester", "Liverpool", "Newcastle"]:
                price_multiplier = random.uniform(0.92, 1.00)
            else:
                price_multiplier = random.uniform(0.95, 1.05)
            
            menu_items_data.append({
                "restaurant_id": rest_id,
                "item_id": item["item_id"],
                "name": item["name"],
                "category": item["category"],
                "price": round(item["price"] * price_multiplier, 2),
                "ingredients": item["ingredients"],
                "is_vegetarian": item["is_vegetarian"],
                "spice_level": item["spice_level"]
            })

    df_menu_items = pd.DataFrame(menu_items_data)
    return df_menu_items

# ============================================
# CUSTOMERS - English Cities
# ============================================
def generate_customers(n=500):
    customers = []
    english_cities = [
        "London", "Manchester", "Birmingham", "Liverpool", "Leeds", 
        "Bristol", "Newcastle", "Sheffield", "Nottingham", "Leicester", 
        "Southampton", "Portsmouth", "York", "Oxford", "Cambridge", "Brighton"
    ]
    
    for i in range(n):
        join_date = fake.date_between(start_date='-2y', end_date='today')
        
        customer = {
            "customer_id": f"CUST-{10000 + i}",
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "city": random.choice(english_cities),
            "join_date": join_date.strftime("%Y-%m-%d"),
        }
        customers.append(customer)
    
    return pd.DataFrame(customers)


def generate_data_for_sql_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.join(script_dir, "data"), exist_ok=True)
    
    df_restaurants = generate_restaurants()
    df_menu_items = generate_menu_items()
    df_customers = generate_customers(500)
    
    df_restaurants.to_csv(os.path.join(script_dir, "data", "restaurants.csv"), index=False)
    df_menu_items.to_csv(os.path.join(script_dir, "data", "menu_items.csv"), index=False)
    df_customers.to_csv(os.path.join(script_dir, "data", "customers.csv"), index=False)

    print(f"Generated {len(df_restaurants)} restaurants")
    print(f"Generated {len(df_menu_items)} menu items")
    print(f"Generated {len(df_customers)} customers")


if __name__ == "__main__":
    generate_data_for_sql_db()