
from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
from urllib.parse import quote

BASE = Path(__file__).resolve().parent
DB = BASE / "travel.db"

app = Flask(__name__)


# --------------------------------------------------
# DESTINATION IMAGE FUNCTION
# --------------------------------------------------


def get_destination_image(name):
    images = {
        "Hyderabad": "photo-1572445271230-a78b5944a659",
        "Warangal": "photo-1606293926075-69a00db0943b",
        "Munnar": "photo-1602216056096-3b40cc0c9944",
        "Alleppey": "photo-1593693411515-c20261bcad6e",
        "Kochi": "photo-1593693411515-c20261bcad6e",
        "Panaji & North Goa": "photo-1512343879784-a960bf40e7f2",
        "Mysuru": "photo-1600112356915-08988c7c9b1e",
        "Ooty": "photo-1597074866923-dc0589150358",
        "Jaipur": "photo-1599661046827-dacff0c0f09a",
        "Agra": "photo-1564507592333-c60657eea523",
        "Manali": "photo-1626621341517-bbf3d9990a23",
        "Darjeeling": "photo-1544735716-392fe2489ffa",
        "Visakhapatnam": "photo-1512343879784-a960bf40e7f2",
        "Tawang": "photo-1464822759023-fed622ff2c3b",
        "Mumbai": "photo-1570168007204-dfb528c6958f",
        "Srinagar": "photo-1464822759023-fed622ff2c3b",
        "Leh": "photo-1464822759023-fed622ff2c3b",
        "Rishikesh": "photo-1464822759023-fed622ff2c3b",
        "New Delhi": "photo-1564507592333-c60657eea523",
        "Puri & Konark": "photo-1512343879784-a960bf40e7f2",
        "Gangtok": "photo-1464822759023-fed622ff2c3b",
    }

    photo_id = images.get(
        name,
        "photo-1470770841072-f978cf4d019e"
    )

    return (
        f"https://images.unsplash.com/{photo_id}"
        "?auto=format&fit=crop&w=1200&q=80"
    )


# --------------------------------------------------
# DESTINATION DATA
# --------------------------------------------------

SAMPLE = [
    ("Telangana", "Hyderabad", "City & heritage", "2 days", 2800,
     "Charminar, Golconda Fort, Hussain Sagar", ""),

    ("Telangana", "Warangal", "History & heritage", "1-2 days", 1800,
     "Warangal Fort, Thousand Pillar Temple, Ramappa Temple", ""),

    ("Kerala", "Munnar", "Hill station & nature", "2 days", 4200,
     "Tea gardens, Eravikulam area, Mattupetty Dam", ""),

    ("Kerala", "Alleppey", "Backwaters", "1-2 days", 3500,
     "Backwaters, Alappuzha Beach, local canals", ""),

    ("Kerala", "Kochi", "Culture & city", "1-2 days", 3200,
     "Fort Kochi, Chinese fishing nets, Mattancherry", ""),

    ("Goa", "Panaji & North Goa", "Beaches & heritage", "3 days", 5200,
     "Panaji, Fort Aguada, Calangute and Baga beaches", ""),

    ("Karnataka", "Mysuru", "Palaces & culture", "2 days", 3000,
     "Mysore Palace, Devaraja Market, Chamundi Hills", ""),

    ("Tamil Nadu", "Ooty", "Hill station", "2-3 days", 4300,
     "Botanical Garden, Ooty Lake, Doddabetta", ""),

    ("Rajasthan", "Jaipur", "Forts & heritage", "2-3 days", 4500,
     "Hawa Mahal, Amber Fort, City Palace", ""),

    ("Uttar Pradesh", "Agra", "Heritage", "1-2 days", 3200,
     "Taj Mahal, Agra Fort, Mehtab Bagh", ""),

    ("Himachal Pradesh", "Manali", "Mountains & adventure", "3-4 days", 6500,
     "Old Manali, Hadimba Temple, Solang Valley", ""),

    ("West Bengal", "Darjeeling", "Hills & tea gardens", "2-3 days", 5000,
     "Tiger Hill, tea gardens, Himalayan Railway area", ""),

    ("Andhra Pradesh", "Visakhapatnam", "Beaches & nature", "2 days", 3000,
     "RK Beach, Kailasagiri, Submarine Museum", ""),

    ("Arunachal Pradesh", "Tawang", "Mountains & monasteries", "4-5 days", 7500,
     "Tawang Monastery, Sela Pass, Madhuri Lake", ""),

    ("Assam", "Guwahati & Kaziranga", "Wildlife & culture", "3 days", 4800,
     "Kamakhya Temple, Brahmaputra riverfront, Kaziranga area", ""),

    ("Bihar", "Bodh Gaya", "Buddhist heritage", "2 days", 2600,
     "Mahabodhi Temple, Great Buddha Statue, monasteries", ""),

    ("Chhattisgarh", "Chitrakote Falls", "Waterfalls & nature", "2 days", 3000,
     "Chitrakote Falls, Tirathgarh Falls, local nature trails", ""),

    ("Gujarat", "Ahmedabad & Statue of Unity", "Heritage & landmarks", "2-3 days", 4200,
     "Sabarmati Ashram, Adalaj Stepwell, Statue of Unity area", ""),

    ("Jharkhand", "Ranchi & Hundru Falls", "Waterfalls & outdoors", "2 days", 2800,
     "Hundru Falls, Rock Garden, Tagore Hill", ""),

    ("Madhya Pradesh", "Khajuraho", "Temples & heritage", "2 days", 3500,
     "Western Group of Temples, Archaeological Museum, local markets", ""),

    ("Maharashtra", "Mumbai", "City & coast", "2-3 days", 4200,
     "Gateway of India, Marine Drive, Elephanta Caves", ""),

    ("Manipur", "Imphal & Loktak Lake", "Culture & lake", "2-3 days", 4000,
     "Kangla Fort, Ima Market, Loktak Lake", ""),

    ("Meghalaya", "Shillong & Cherrapunji", "Waterfalls & hills", "3 days", 4800,
     "Umiam Lake, Nohkalikai Falls, living root bridge area", ""),

    ("Mizoram", "Aizawl", "Hills & local culture", "2 days", 3500,
     "Durtlang Hills, Solomon Temple, local markets", ""),

    ("Nagaland", "Kohima", "Hills & culture", "2-3 days", 4200,
     "Kohima War Cemetery, Kisama Heritage Village, viewpoints", ""),

    ("Odisha", "Puri & Konark", "Temple & beach", "2-3 days", 3600,
     "Jagannath Temple area, Puri Beach, Konark Sun Temple", ""),

    ("Punjab", "Amritsar", "Culture & food", "2 days", 3000,
     "Golden Temple, Jallianwala Bagh, Partition Museum", ""),

    ("Sikkim", "Gangtok", "Mountains & monasteries", "3 days", 5200,
     "MG Marg, Rumtek Monastery, Tsomgo Lake (permit/weather dependent)", ""),

    ("Tripura", "Agartala", "Palaces & heritage", "2 days", 2800,
     "Ujjayanta Palace, Neermahal (day trip), heritage museum", ""),

    ("Uttarakhand", "Rishikesh", "River & mountains", "2-3 days", 4000,
     "Triveni Ghat, Beatles Ashram area, riverfront, nearby viewpoints", ""),

    ("Haryana", "Kurukshetra", "Heritage & spirituality", "1-2 days", 2300,
     "Brahma Sarovar, Jyotisar, Kurukshetra Panorama", ""),

    ("Andaman and Nicobar Islands", "Swaraj Dweep (Havelock)",
     "Island & beaches", "3-4 days", 8500,
     "Radhanagar Beach, island viewpoints, permitted water activities", ""),

    ("Chandigarh", "Chandigarh city", "Gardens & architecture", "1-2 days", 2600,
     "Rock Garden, Sukhna Lake, Capitol Complex (access rules apply)", ""),

    ("Dadra and Nagar Haveli and Daman and Diu", "Diu",
     "Coast & heritage", "2 days", 3200,
     "Diu Fort, Nagoa Beach, St. Paul's Church", ""),

    ("Delhi", "New Delhi", "Capital & heritage", "2-3 days", 3800,
     "India Gate, Qutub Minar, Humayun's Tomb, Red Fort area", ""),

    ("Jammu and Kashmir", "Srinagar", "Lakes & mountains", "3-4 days", 7000,
     "Dal Lake, Mughal Gardens, old city, viewpoints", ""),

    ("Ladakh", "Leh", "High-altitude landscapes", "4-5 days", 9000,
     "Leh Palace, Shanti Stupa, monasteries, acclimatisation day", ""),

    ("Lakshadweep", "Agatti Island", "Island & lagoon", "3-4 days", 11000,
     "Lagoon viewpoints, approved beach activities, island excursions", ""),

    ("Puducherry", "Puducherry town", "Coast & French heritage", "2 days", 3500,
     "Promenade Beach, White Town, Auroville visitor area", ""),
]


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                duration TEXT,
                base_budget REAL,
                attractions TEXT,
                image_url TEXT
            )
        """)

        count = con.execute(
            "SELECT COUNT(*) FROM destinations"
        ).fetchone()[0]

        if count == 0:
            con.executemany("""
                INSERT INTO destinations
                (state, name, category, duration, base_budget,
                 attractions, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, SAMPLE)

        # User profiles
        con.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Support messages
        con.execute("""
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Update images for all existing destinations.
        # Existing destination IDs and other data are preserved.
        destinations = con.execute(
            "SELECT id, name, image_url FROM destinations"
        ).fetchall()

        for dest in destinations:
            con.execute("""
                UPDATE destinations
                SET image_url = ?
                WHERE id = ?
            """, (get_destination_image(dest["name"]), dest["id"]))


# --------------------------------------------------
# CONVERT DATABASE ROWS TO DICTIONARIES
# --------------------------------------------------
init_db()
def rows_to_dict(rows):
    results = []

    for row in rows:
        item = dict(row)

        # Always use the destination-specific image URL.
        item["image_url"] = get_destination_image(item["name"])

        results.append(item)

    return results


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    with connect() as con:
        destinations = rows_to_dict(
            con.execute(
                "SELECT * FROM destinations ORDER BY state, name"
            ).fetchall()
        )

        states = [
            row[0]
            for row in con.execute(
                "SELECT DISTINCT state FROM destinations ORDER BY state"
            ).fetchall()
        ]

    return render_template(
        "index.html",
        destinations=destinations,
        states=states
    )


# --------------------------------------------------
# DESTINATION SEARCH API
# --------------------------------------------------

@app.get("/api/destinations")
def api_destinations():
    state = request.args.get("state", "").strip()
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    sql = "SELECT * FROM destinations WHERE 1=1"
    args = []

    if state:
        sql += " AND state = ?"
        args.append(state)

    if q:
        sql += """
            AND (name LIKE ? OR attractions LIKE ? OR state LIKE ?)
        """
        args.extend([f"%{q}%"] * 3)

    if category:
        sql += " AND category LIKE ?"
        args.append(f"%{category}%")

    sql += " ORDER BY state, name"

    with connect() as con:
        results = con.execute(sql, args).fetchall()

    return jsonify(rows_to_dict(results))


# --------------------------------------------------
# TRIP BUDGET CALCULATOR API
# --------------------------------------------------

@app.post("/api/calculate")
def calculate():
    try:
        data = request.get_json(silent=True) or {}

        people = max(1, min(50, int(data.get("people", 1))))
        days = max(1, min(30, int(data.get("days", 2))))

    except (TypeError, ValueError):
        return jsonify({
            "error": "Please enter valid people and days."
        }), 400

    budget_type = data.get("budget_type", "ultra")
    destination = str(data.get("destination", "")).strip()
    start = str(data.get("start", "Hyderabad")).strip() or "Hyderabad"

    with connect() as con:
        dest = con.execute(
            "SELECT * FROM destinations WHERE name = ?",
            (destination,)
        ).fetchone()

    if not dest:
        return jsonify({
            "error": "Please choose a destination from the list."
        }), 400

    factors = {
        "ultra": 0.78,
        "budget": 1.0,
        "comfortable": 1.45
    }

    if budget_type not in factors:
        budget_type = "ultra"

    factor = factors[budget_type]
    base = float(dest["base_budget"]) * factor

    transport = round(base * 0.30)

    room_rate = (
        450 if budget_type == "ultra"
        else 650 if budget_type == "budget"
        else 1200
    )

    food_rate = (
        250 if budget_type == "ultra"
        else 350 if budget_type == "budget"
        else 600
    )

    local_rate = (
        180 if budget_type == "ultra"
        else 300 if budget_type == "budget"
        else 550
    )

    ticket_rate = (
        100 if budget_type == "ultra"
        else 180 if budget_type == "budget"
        else 350
    )

    room = round(max(0, days - 1) * room_rate / 2)
    food = round(days * food_rate)
    local = round(days * local_rate)
    tickets = round(days * ticket_rate)
    other = round(days * 100)

    per_person = transport + room + food + local + tickets + other

    attractions = [
        item.strip()
        for item in (dest["attractions"] or "").split(",")
        if item.strip()
    ]

    itinerary = []

    for day in range(1, days + 1):
        if day == 1:
            task = (
                f"Travel from {start} to {destination}, "
                "check in, and explore nearby places."
            )

        elif day == days:
            task = (
                f"Visit remaining sights in {destination}, "
                "keep time for meals, and begin return travel."
            )

        else:
            place = (
                attractions[(day - 2) % len(attractions)]
                if attractions else destination
            )

            task = (
                f"Explore {place}; use local buses/shared transport "
                "and leave time for lunch and evening sightseeing."
            )

        itinerary.append({
            "day": day,
            "task": task
        })

    return jsonify({
        "start": start,
        "destination": destination,
        "state": dest["state"],
        "people": people,
        "days": days,
        "budget_type": budget_type,
        "transport": transport,
        "room": room,
        "food": food,
        "local_transport": local,
        "tickets": tickets,
        "other": other,
        "per_person": per_person,
        "group_total": per_person * people,
        "itinerary": itinerary,
        "note": (
            "Planning estimate only; actual fares, rooms, tickets "
            "and seasonal prices may differ."
        )
    })


# --------------------------------------------------
# ABOUT PAGE
# --------------------------------------------------

@app.route("/about")
def about():
    return render_template("about.html")


# --------------------------------------------------
# PROFILE CREATION
# --------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():
    message = ""
    profile_data = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not email:
            message = "Please enter your name and email."

        elif (
            len(name) > 80
            or len(email) > 120
            or len(phone) > 20
        ):
            message = "Please check the length of your details."

        elif "@" not in email or "." not in email.split("@")[-1]:
            message = "Please enter a valid email address."

        else:
            try:
                with connect() as con:
                    con.execute("""
                        INSERT INTO profiles (name, email, phone)
                        VALUES (?, ?, ?)
                    """, (name, email, phone))

                message = "Profile created successfully!"

            except sqlite3.Error:
                app.logger.exception("Could not save profile")
                message = "Unable to save profile. Please try again."

    with connect() as con:
        profile_data = con.execute("""
            SELECT id, name, email, phone, created_at
            FROM profiles
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

    return render_template(
        "profile.html",
        message=message,
        profile_data=profile_data
    )


# --------------------------------------------------
# SUPPORT / CONTACT PAGE
# --------------------------------------------------

@app.route("/support", methods=["GET", "POST"])
def support():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        user_message = request.form.get("message", "").strip()

        if not name or not email or not user_message:
            message = "Please fill in all required fields."

        elif (
            len(name) > 80
            or len(email) > 120
            or len(user_message) > 2000
        ):
            message = "One or more fields are too long."

        elif "@" not in email or "." not in email.split("@")[-1]:
            message = "Please enter a valid email address."

        else:
            try:
                with connect() as con:
                    con.execute("""
                        INSERT INTO support_messages (name, email, message)
                        VALUES (?, ?, ?)
                    """, (name, email, user_message))

                message = (
                    "Your message has been submitted successfully!"
                )

            except sqlite3.Error:
                app.logger.exception("Could not save support message")
                message = (
                    "Unable to submit your message. Please try again."
                )

    return render_template("support.html", message=message)


# --------------------------------------------------
# DESTINATION DETAILS PAGE
# --------------------------------------------------

@app.route("/destination/<int:destination_id>")
def destination_details(destination_id):
    with connect() as con:
        dest = con.execute(
            "SELECT * FROM destinations WHERE id = ?",
            (destination_id,)
        ).fetchone()

    if dest is None:
        return "Destination not found", 404

    attractions = [
        place.strip()
        for place in (dest["attractions"] or "").split(",")
        if place.strip()
    ]

    image_url = get_destination_image(dest["name"])
    # Sample 3-day itinerary
    day_plan = []

    for day in range(1, 4):
        if attractions:
            place1 = attractions[(day - 1) % len(attractions)]
            place2 = attractions[(day) % len(attractions)]
        else:
            place1 = dest["name"]
            place2 = dest["name"]

        if day == 1:
            morning = "Reach the destination and check in to your stay."
            afternoon = f"Explore {place1}."
            evening = "Enjoy a local market or nearby sightseeing."
        elif day == 2:
            morning = f"Visit {place1}."
            afternoon = f"Explore {place2}."
            evening = "Try local food and enjoy the evening."
        else:
            morning = f"Visit {place1} or another nearby attraction."
            afternoon = "Shopping, photography, or relaxed sightseeing."
            evening = "Check out and plan your return journey."

        day_plan.append({
            "day": day,
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening
        })

    # Example stay prices per room per night
    hotel_options = [
        {
            "name": "Budget Stay",
            "price": "₹500–₹1,000",
            "description": "Basic room or budget guesthouse"
        },
        {
            "name": "Standard Hotel",
            "price": "₹1,200–₹2,500",
            "description": "Private room with basic facilities"
        },
        {
            "name": "Comfort Stay",
            "price": "₹2,500+",
            "description": "More comfort and additional facilities"
        }
    ]

    # General transport suggestions
    transport_options = [
        {
            "name": "Train",
            "description": "Useful for intercity travel; fare depends on route and class."
        },
        {
            "name": "Bus",
            "description": "Compare state bus and private bus options."
        },
        {
            "name": "Local Transport",
            "description": "Use local buses, shared autos, or cabs as available."
        }
    ]

    # Illustrative food budget per person per day
    food_budget = [
        {
            "name": "Budget Food",
            "price": "₹250–₹400 per day",
            "description": "Local eateries, breakfast and simple meals"
        },
        {
            "name": "Standard Food",
            "price": "₹400–₹700 per day",
            "description": "A mix of local restaurants and cafes"
        }
    ]

    local_transport_budget = "₹200–₹500 per person per day (sample estimate)"
    return render_template(
        "destination.html",
        dest=dest,
        attractions=attractions,
        image_url=image_url
    )
    return render_template(
        "destination.html",
        dest=dest,
        attractions=attractions,
        day_plan=day_plan,
        hotel_options=hotel_options,
        transport_options=transport_options,
        food_budget=food_budget,
        local_transport_budget=local_transport_budget
    )

# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
