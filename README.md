# SeaFishPick — Coastal Fish-Pickle Storefront

A starter full-stack e-commerce project for a fish-pickle brand inspired by the Kanyakumari–Colachel–Muttom coastline of Tamil Nadu. It uses FastAPI, SQLModel, SQLite, Jinja2, HTML, CSS and vanilla JavaScript, with a modular MVC-style layout intended for learning and editing in PyCharm.

> **Prototype disclaimer:** Product descriptions, prices, ratings, reviews, stock levels and demo contact information are examples. They are not real customer endorsements or confirmed food-label information. Checkout records a demo order only; no real payment is processed. Before selling food, replace sample copy with verified ingredients, allergen/storage information, applicable food-label details and real product photographs.

## Features

- Homepage with coastal storytelling, a product catalogue and responsive navigation.
- Product detail pages with ingredients, weight, spice level, stock, ratings, reviews and related products.
- Search, category, price range, minimum rating, spice level, availability and sorting filters.
- Guest cart and wishlist held in the signed session, with persistent cart/wishlist for signed-in customers.
- Registration, login, logout, profile editing and password hashing with PBKDF2-SHA256.
- Demo checkout supporting Cash on Delivery and a clearly marked non-transactional online-payment demo option.
- Order list, order detail, stock decrement on successful demo orders, and statuses: Pending, Confirmed, Packed, Shipped, Delivered and Cancelled.
- Owner/admin dashboard with summary metrics, low-stock items and best-seller data.
- Product create/edit/deactivate, category create/edit/delete-or-deactivate, order management, customer summaries, inventory and review pages.
- Demo seed data: one admin, one customer, five categories, seven products and illustrative reviews.
- Static SVG artwork so the site still looks reasonable if an external reference image cannot load.

## Technology

- Python 3.14 target
- FastAPI and Uvicorn
- SQLModel / Pydantic
- SQLite 3
- Jinja2 templates
- HTML5, CSS3 and vanilla JavaScript

No React, Vue, Angular or other JavaScript UI framework is used. Dependency versions in `requirements.txt` are ranges so pip can resolve compatible releases for your Python installation; Python 3.14 compatibility depends on the installed release of each dependency.

## Project structure

```text
SeaFishPick/
├── app/
│   ├── main.py
│   ├── controllers/       # shared template/controller helpers
│   ├── core/              # Jinja2 configuration
│   ├── database/          # SQLite engine and seed data
│   ├── models/            # SQLModel tables
│   ├── routers/           # FastAPI route handlers
│   ├── services/          # authentication, catalogue, cart and order logic
│   ├── static/
│   │   ├── css/            # storefront, responsive and admin styles
│   │   ├── images/         # local SVG fallback and brand artwork
│   │   └── js/             # vanilla JavaScript
│   └── templates/          # Jinja2 storefront and admin pages
├── database/               # SQLite database is created here on first run
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Run in PyCharm

1. Open the `SeaFishPick` folder as a project.
2. Configure a Python 3.14 interpreter (or use a Python version supported by the resolved dependencies).
3. Create and activate a virtual environment in the project root.
4. Open the PyCharm terminal and install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the development server from the project root:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open `http://127.0.0.1:8000` in your browser. FastAPI's interactive API docs are at `http://127.0.0.1:8000/docs`; `/health` provides a basic health response.

The SQLite database is created automatically at `database/seafishpick.db`. Tables and sample data are set up at application startup. The database file is generated locally and excluded from source control by `.gitignore`.

### Demo sign-in accounts

| Role | Email | Password |
|---|---|---|
| Admin | `admin@seafishpick.local` | `Admin@123` |
| Customer | `customer@example.com` | `Customer@123` |

These credentials are for local demonstration only. Change them and replace `SECRET_KEY` before exposing the application to anyone else. The demo admin is seeded automatically for convenience, which is not a suitable production provisioning approach.

## Database and demo orders

The application initializes tables using SQLModel and SQLite. The seed function inserts demo records only when the matching account/product/category records do not already exist. A successful checkout creates an order and line items, decrements stock and empties the user's basket. The payment status remains `Demo only`; no card details, payment gateway or real transaction is involved.

To reset your local demo data, stop Uvicorn and delete `database/seafishpick.db`. Restarting the app recreates the tables and demo records. **This deletes local demo orders and changes, so back up the database first if you need to keep them.**

## Images, image credits and fallbacks

The project uses original local SVG illustrations in `app/static/images/` as resilient fallbacks. In the templates and seed data, external photo references point to Wikimedia Commons pages/files for:

- [Kanyakumari fishing boats — Commons file page](https://commons.wikimedia.org/wiki/File:01FishingBoats%26Kanyakumari.jpg)
- [Homemade Indian pickles — Commons file page](https://commons.wikimedia.org/wiki/File:Jars_filled_with_homemade_Indian_pickles.jpg)
- [Kanyakumari beach — Commons file page](https://commons.wikimedia.org/wiki/File:Kanyakumari_beach.jpg)

Those photos are used as regional/story references, not represented as SeaFishPick's own products. Remote image redirects and their licensing/attribution terms can change; review each current Commons file page and satisfy its licence before commercial use. For launch, it is preferable to use your own approved beach/fishing photography and photographs of your actual packaged products. Change the `image_url` values in `app/database/seed.py` and admin product form as needed.

## Important before production

- Replace `SECRET_KEY`; configure `COOKIE_SECURE=1` behind HTTPS and review session settings.
- Add CSRF protection to state-changing form posts, rate limiting, email verification and appropriate password reset flows.
- Review admin-user provisioning, logging and access controls.
- Add real payment integration only after the store's business and compliance requirements are established.
- Verify food ingredients, allergens, net quantity, batch/date, storage, shelf-life and any applicable FSSAI/business requirements with qualified local guidance.
- Use real product photography and confirm image permissions/attribution.
- Add automated tests, migrations and production deployment configuration before handling real customers.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'sqlmodel'`:** Select the project's virtual environment in PyCharm and run `pip install -r requirements.txt` in that same interpreter.
- **Database schema is stale:** back up your database. For this prototype, easiest reset is to stop the server and delete `database/seafishpick.db`, then restart. A production app should use migration tooling instead.
- **Images don't load:** check the network and original Wikimedia file page. Each major image has a local SVG fallback; use local image paths when you have approved assets.
- **Admin page redirects to login:** sign in with the local demo admin account above.
- **Port already in use:** start on another port, e.g. `uvicorn app.main:app --reload --port 8001`.

## Notes

This is an educational starter codebase, not a security-audited production commerce platform. Use it as a learning foundation and verify the dependency releases that pip resolves for your specific Python 3.14 installation.
