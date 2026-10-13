# Smart Travel Planner

A beginner-friendly Flask + SQLite starter website for budget travel planning in India.

## Features
- Responsive home page and destination cards
- Search and state/category filters
- Sample destination database seeded automatically
- Ultra-budget, budget and comfortable estimates
- Editable starting location, traveller count and trip duration
- Expense breakdown and simple day-wise itinerary
- About page

## Run locally

1. Install Python 3.10+ and open this folder in VS Code.
2. Create and activate a virtual environment:
   - Windows PowerShell: `python -m venv venv` then `.\\venv\\Scripts\\Activate.ps1`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the app: `python app.py`
5. Open `http://127.0.0.1:5000` in your browser.

The SQLite database `travel.db` is created automatically at first launch.

## Add destinations

Edit the `SAMPLE` list near the top of `app.py`. Each row is:
`(state, name, category, duration, base_budget, attractions, image_url)`

For production, move the seed data into a JSON/CSV import process or admin interface. Use image URLs you have permission to use.

## Important notes
- The seed list now includes one representative sample destination for each of India’s 28 states and 8 Union Territories. Add more destinations per region by editing `SAMPLE` in `app.py`. Images are illustrative remote image URLs and should be replaced with verified/licensed destination photos before public release.
- Costs are demonstration estimates, not live quotes. Transport, room, food, local travel and tickets are calculated from sample rules. Verify current fares and fees before travel.
- The “Smart Travel Assistant” area is currently a prompt/demo strip, not a connected AI chatbot. A real AI integration needs a server-side API key and suitable provider/API.
- Route distances, live maps, real train/bus schedules, hotel listings, user login and booking integrations are not implemented in this starter.
- Do not expose API keys in frontend JavaScript. Add validation, rate limits, logging and production configuration before public deployment.
