import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('test_db')
cursor = conn.cursor()

df = pd.read_csv('Nepal_Final_Analysis_2026.csv')

df.to_sql('cities', conn, if_exists='replace', index=False)

# Data visualization


def show_graphical_view(data_rows):
    # data_rows comes from cursor.fetchall() which is a list of tuples
    # We turn it back into a DataFrame to make graphing easy
    columns = ['City', 'Avg_Wage', 'Rent', 'Milk', 'Internet', 'Food',
               'Monthly_Tax', 'Take_Home_Pay', 'Total_Costs', 'Monthly_Surplus']
    temp_df = pd.DataFrame(data_rows, columns=columns)

    colors = ['green' if x > 0 else 'red' for x in temp_df['Monthly_Surplus']]
    plt.figure(figsize=(12, 6))
    plt.bar(temp_df['City'], temp_df['Monthly_Surplus'], color=colors)
    plt.axhline(0, color='black', linewidth=1.5)
    plt.xticks(rotation=45)
    plt.title('Livability Index: Monthly Surplus by City')
    plt.ylabel('NPR')
    plt.tight_layout()
    print("📊 Opening graph window...")
    plt.show()

# --- THE UPGRADED TAX ENGINE ---


def calculate_nepal_tax(monthly_salary):
    annual_salary = monthly_salary * 12
    tax = 0

    # Slab 1: First 500k at 1%
    if annual_salary <= 500000:
        tax = annual_salary * 0.01
    # Slab 2: Next 200k (up to 700k) at 10%
    elif annual_salary <= 700000:
        tax = (500000 * 0.01) + (annual_salary - 500000) * 0.10
    # Slab 3: Next 300k (up to 1M) at 20%
    else:
        tax = (500000 * 0.01) + (200000 * 0.10) + \
            (annual_salary - 700000) * 0.20

    return tax / 12  # Convert back to monthly tax


def show_menu():

    print("\n" + "="*30)
    print("🏢 NEPAL CITY MANAGER")
    print("="*30)
    print("1. View All Cities")
    print("2. Search for a City")
    print("3. Add a New City")
    print("4. Update City Rent")
    print("5. Delete a City")
    print("6. Exit")
    print("="*30)


while True:
    show_menu()
    choice = input("Select an option (1-6): ")

    if choice == '1':
        # 1. Fetch all data
        cursor.execute("SELECT * FROM cities")
        rows = cursor.fetchall()

        print("\n" + "="*145)
        # HEADER LINE: Using specific widths to keep it organized
        # Wage, Rent, Milk, Int, Food, Tax, Pay, Cost, Surplus
        print(f"{'City':<12} | {'Wage':<8} | {'Rent':<6} | {'Milk':<5} | {'Int':<5} | {'Food':<6} | {'Tax':<7} | {'Pay':<8} | {'Cost':<7} | {'Surplus':<9}")
        print("-" * 145)

        # 2. DATA ROWS: Matching the widths from the header
        for r in rows:
            # round() is used to keep the decimals from getting too long
            print(f"{r[0]:<12} | "      # City
                  f"{r[1]:<8} | "      # Avg_Wage
                  f"{r[2]:<6} | "      # Rent
                  f"{r[3]:<5} | "      # Milk
                  f"{r[4]:<5} | "      # Internet
                  f"{r[5]:<6} | "      # Food
                  f"{round(r[6], 2):<7} | "  # Monthly_Tax (rounded)
                  f"{round(r[7], 2):<8} | "  # Take_Home_Pay (rounded)
                  f"{round(r[8], 2):<7} | "  # Total_Costs (rounded)
                  f"{round(r[9], 2):<9}")   # Monthly_Surplus (rounded)

        print("="*145)

        if rows:
            graph_choice = input(
                "\nWould you like to see a graphical comparison? (y/n): ").lower()
            if graph_choice == 'y':
                show_graphical_view(rows)

    elif choice == '2':
        search_term = input("Enter city name to search for: ")

        # We wrap the search term in % so it finds partial matches
        # Example: '%kath%' will find 'Kathmandu'
        formatted_search = f"%{search_term}%"

        query = "SELECT * FROM cities WHERE City LIKE ?"
        cursor.execute(query, (formatted_search,))
        results = cursor.fetchall()

        if results:
            print(f"\n--- Found {len(results)} match(es) ---")
            for r in results:
                # Using our professional alignment again
                print(
                    f"📍 {r[0]:<12} | Wage: {r[1]:<7} | Rent: {r[2]:<6} | Surplus: {r[9]:<8}")
        else:
            print(f"❌ No cities found matching '{search_term}'")

    elif choice == '3':
        name = input("Enter City Name:")
        avg_wage = float(input("Enter Monthly Wage:"))
        rent = float(input("Enter Monthly Rent:"))
        milk = float(input("Enter Milk Price per ltr:"))
        internet = float(input("Enter Intenet bill:"))
        food = float(input("Enter Food Expenses:"))

        # Run the G-Engine Logic
        monthly_tax = calculate_nepal_tax(avg_wage)
        take_home_pay = avg_wage - monthly_tax

        # Calculation: Rent + Internet + Food + (Milk * 30 liters)
        total_costs = rent + internet + food + (milk * 30)
        monthly_surplus = take_home_pay - total_costs

        query_1 = """
        INSERT INTO cities(City, Avg_Wage, Rent, Milk, Internet, Food, Monthly_Tax, Take_Home_Pay, Total_Costs, Monthly_Surplus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        data_tuple = (
            name, avg_wage, rent, milk, internet, food,
            monthly_tax, take_home_pay, total_costs, monthly_surplus
        )

        cursor.execute(query_1, data_tuple)
        conn.commit()
        print(
            f"\n✅ {name} added! Monthly Tax calculated: Rs{round(monthly_tax, 2)}")

    elif choice == '4':
        city_to_update = input(
            "Enter the name of the city you want to update: ")

        # 1. Fetch current data for this city
        cursor.execute(
            "SELECT Avg_Wage, Milk, Internet, Food FROM cities WHERE City = ?", (city_to_update,))
        row = cursor.fetchone()

        if row:
            # Unpack the current data
            avg_wage, milk, internet, food = row

            # 2. Get the new Rent
            new_rent = float(
                input(f"Current city found. Enter new Monthly Rent for {city_to_update}: "))

            # 3. RE-RUN THE G-ENGINE
            monthly_tax = calculate_nepal_tax(avg_wage)
            take_home_pay = avg_wage - monthly_tax
            # Recalculate costs with the NEW rent
            new_total_costs = new_rent + internet + food + (milk * 30)
            new_surplus = take_home_pay - new_total_costs

            # 4. UPDATE DATABASE
            update_query = """
            UPDATE cities 
            SET Rent = ?, Monthly_Surplus = ?, Total_Costs = ?
            WHERE City = ?
            """
            cursor.execute(update_query, (new_rent, new_surplus,
                           new_total_costs, city_to_update))
            conn.commit()

            print(
                f"✅ Success! {city_to_update} updated. New Surplus: {round(new_surplus, 2)}")
        else:
            print("❌ City not found in database!")

    elif choice == '5':
        print("\n--- 🗑️ DELETE CITY RECORD ---")
        city_to_delete = input(
            "Enter the name of the city you want to REMOVE: ")

        # 1. First, we check if the city even exists
        cursor.execute("SELECT City FROM cities WHERE City = ?",
                       (city_to_delete,))
        result = cursor.fetchone()

        if result:
            # 2. The Confirmation Step (Safety First!)
            confirm = input(
                f"Are you SURE you want to delete {city_to_delete}? This cannot be undone! (yes/no): ").lower()

            if confirm == 'yes':
                # 3. The actual DELETE command
                cursor.execute(
                    "DELETE FROM cities WHERE City = ?", (city_to_delete,))
                conn.commit()
                print(
                    f"✅ Success! {city_to_delete} has been wiped from the database.")
            else:
                print("Operation cancelled. Data is safe.")
        else:
            print(f"❌ Error: '{city_to_delete}' not found in our records.")

    elif choice == '6':
        print("\nClosing system. Goodbye, Rj!")
        conn.close()
        break  # This breaks the loop and ends the program

    else:
        print("\n❌ Invalid choice! Please pick 1-5.")
