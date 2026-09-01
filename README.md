# Surveil The Bulk

> *"Look at the top cards of your library. Put any number of them into your graveyard and the rest back on top in any order."*

**Surveil The Bulk** is a specialized REST API for Magic: The Gathering players. It goes beyond simple inventory tracking by focusing on **collection analysis, seamless wantlist/tradelist sharing, and advanced deckbuilding**. 

## 🚀 Core Features

* **Smart Inventory & Lists:** Categorize your collection into `own`, `want`, and `trade`.
* **List Sharing (WIP):** Designed to easily export and share your wantlists and tradelists with other players or local game stores.
* **Relational Deckbuilding:** Bind physical cards from your inventory directly to specific decks (e.g., know exactly which Commander deck is currently holding your *Sol Ring*).
* **Automated Card Data:** Built-in integration with the Scryfall API to fetch real-time card data, Oracle text, and image URLs.
* **High Performance:** Asynchronous backend powered by Python and `aiohttp`.

## 🛠️ Tech Stack


## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ArthurSVieira/MagicTheCollection.git](https://github.com/ArthurSVieira/MagicTheCollection.git)
   cd MagicTheCollection
   ```

2. **Install dependencies:**
   ```bash
   pip install aiohttp requests
   ```


## 📡 API Endpoints

### System
* `GET /api/status` - Check if the API is online and its current version.

### Collection & Lists
* `GET /api/cards?filter={all|bulk|trade|want}` - Fetch your collection. Ideal for generating shareable tradelists or wantlists.
* `POST /api/cards` - Add or update card quantities in your inventory.

### Deckbuilding
* `GET /api/decks` - List all created decks.
* `POST /api/decks` - Create a new deck (requires `name`, `format`, `color_ident`).
* `GET /api/decks/cards?deck={deck_name}` - View the exact decklist for a specific deck.
* `POST /api/decks/cards` - Allocate a card from your inventory to a specific deck.

## 📝 License

Developed by Arthur.
