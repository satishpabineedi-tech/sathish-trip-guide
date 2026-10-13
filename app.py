
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from urllib.parse import quote

BASE = Path(__file__).resolve().parent
DB = BASE / "travel.db"

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-key-change-before-deploying"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# --------------------------------------------------
# DESTINATION IMAGE FUNCTION
# --------------------------------------------------




def get_destination_image(name):
    images = {
        "Swaraj Dweep (Havelock)": "swaraj-dweep-havelock.jpg",
        "Visakhapatnam": "visakhapatnam.jpg",
        "Tawang": "tawang.jpg",
        "Guwahati & Kaziranga": "guwahati-kaziranga.jpg",
        "Bodh Gaya": "bodh-gaya.jpg",
        "Chandigarh": "chandigarh.jpg",
        "Chandigarh city": "chandigarh.jpg",
        "Chitrakote Falls": "chitrakote-falls.jpg",
        "Diu": "diu.jpg",
        "New Delhi": "new-delhi.jpg",
        "Panaji & North Goa": "panaji-north-goa.jpg",
        "Ahmedabad & Statue of Unity": "ahmedabad-statue-of-unity.jpg",
        "Kurukshetra": "kurukshetra.jpg",
        "Manali": "manali.jpg",
        "Srinagar": "srinagar.jpg",
        "Mysuru": "mysuru.jpg",
        "Alleppey": "alleppey.jpg",
        "Kochi": "kochi.jpg",
        "Munnar": "munnar.jpg",
        "Leh": "leh.jpg",
        "Mumbai": "mumbai.jpg",
        "Shillong & Cherrapunji": "shillong-cherrapunji.jpg",
        "Ranchi & Hundru Falls": "hundru-falls.jpg",
        "Agatti Island": "agatti_island.jpg",
        "Khajuraho": "khajuraho.jpg",
        "Imphal & Loktak Lake": "loktak_lake.jpg",
        "Aizawl": "aizawl.jpg",
        "Kohima": "kohima.jpg",
        "Puri & Konark": "puri_konark.jpg",
        "Puducherry Town": "puducherry.jpg",
        "Puducherry town": "puducherry.jpg",
        "Amritsar": "amritsar.jpg",
        "Jaipur": "jaipur.jpg",
        "Gangtok": "gangtok.jpg",
        "Ooty": "ooty.jpg",
        "Hyderabad": "hyderabad.jpg",
        "Warangal": "warangal.jpg",
        "Agartala": "agartala.jpg",
        "Agra": "agra.jpg",
        "Rishikesh": "rishikesh.jpg",
        "Darjeeling": "darjeeling.jpg",
    }

    filename = images.get(name, "home.jpg")
    image_path = BASE / "static" / "images" / filename

    if image_path.is_file():
        return f"/static/images/{filename}"

    return "/static/images/home.jpg"

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
    try:
        with connect() as con:

            # 1. Destinations table
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

            # 2. Users table
            con.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Create profiles table before checking its columns
            con.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Add user_id only if it does not exist
            profile_columns = {
                row["name"]
                for row in con.execute(
                    "PRAGMA table_info(profiles)"
                ).fetchall()
            }

            if "user_id" not in profile_columns:
                con.execute("""
                    ALTER TABLE profiles
                    ADD COLUMN user_id INTEGER REFERENCES users(id)
                """)

            # 5. One profile per registered user
            con.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_user_id
                ON profiles(user_id)
                WHERE user_id IS NOT NULL
            """)

            # 6. Support messages table
            con.execute("""
                CREATE TABLE IF NOT EXISTS support_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 7. Add sample destinations only if the table is empty
            count = con.execute(
                "SELECT COUNT(*) FROM destinations"
            ).fetchone()[0]

            if count == 0:
                con.executemany("""
                    INSERT INTO destinations (
                        state,
                        name,
                        category,
                        duration,
                        base_budget,
                        attractions,
                        image_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, SAMPLE)

            # 8. Refresh image paths without deleting destinations
            destinations = con.execute(
                "SELECT id, name FROM destinations"
            ).fetchall()

            for dest in destinations:
                image_path = get_destination_image(dest["name"])

                con.execute("""
                    UPDATE destinations
                    SET image_url = ?
                    WHERE id = ?
                """, (image_path, dest["id"]))

        print("Database initialized successfully.")

    except sqlite3.Error as error:
        print(f"Database initialization error: {error}")
        raise


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


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            message = "Please fill in all required fields."

        elif len(name) > 80 or len(email) > 120 or len(phone) > 20:
            message = "Please check the length of your details."

        elif "@" not in email or "." not in email.split("@")[-1]:
            message = "Please enter a valid email address."

        elif len(password) < 8:
            message = "Password must be at least 8 characters."

        else:
            try:
                password_hash = generate_password_hash(password)

                with connect() as con:
                    cursor = con.execute("""
                        INSERT INTO users
                            (name, email, password_hash)
                        VALUES (?, ?, ?)
                    """, (name, email, password_hash))

                    user_id = cursor.lastrowid

                    con.execute("""
                        INSERT INTO profiles
                            (user_id, name, email, phone)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, name, email, phone))

                session.clear()
                session["user_id"] = user_id

                return redirect(url_for("profile"))

            except sqlite3.IntegrityError:
                message = "This email is already registered. Please log in."

    return render_template("signup.html", message=message)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with connect() as con:
            user = con.execute("""
                SELECT id, name, email, password_hash
                FROM users
                WHERE email = ? COLLATE NOCASE
            """, (email,)).fetchone()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))

        message = "Incorrect email or password."

    return render_template("login.html", message=message)


# --------------------------------------------------
# PROFILE: LOGIN REQUIRED
# --------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    message = ""

    with connect() as con:
        user = con.execute("""
            SELECT id, name, email
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()

            if not name:
                message = "Please enter your name."

            elif len(name) > 80 or len(phone) > 20:
                message = "Please check the length of your details."

            else:
                con.execute("""
                    UPDATE users
                    SET name = ?
                    WHERE id = ?
                """, (name, user_id))

                con.execute("""
                    UPDATE profiles
                    SET name = ?, phone = ?
                    WHERE user_id = ?
                """, (name, phone, user_id))

                message = "Profile updated successfully!"

        profile_data = con.execute("""
            SELECT id, name, email, phone, created_at
            FROM profiles
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return render_template(
        "account.html",
        user=user,
        profile_data=profile_data,
        message=message
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



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
