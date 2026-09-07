from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from surveil_the_bulk.db import (
    add_card_to_deck,
    add_deck,
    show_decklist,
    update_inventory,
    view_colection,
    view_decks,
)



pageRouter = APIRouter()
apiRouter = APIRouter(prefix="/api") 



@pageRouter.get("/", response_class=HTMLResponse, include_in_schema = False)
def home():
    return f"<h1>This is the home page!<h1>"


class CollectionRequest(BaseModel):
    name: str
    own_qty: int = 0
    wnt_qty: int = 0
    trd_qty: int = 0


@apiRouter.post("/cards")
def update_collection(dados: CollectionRequest):
    update_inventory(
        dados.name,
        dados.own_qty, 
        dados.wnt_qty, 
        dados.trd_qty
    )
    return  "Colecao atualizada com sucesso"

class DeckRequest(BaseModel):
    name: str
    format: str
    color: str 

@apiRouter.post("/decks")
def create_deck(deck: DeckRequest):
    add_deck(deck.name, 
    deck.format, 
    deck.color
    )
    return "Deck adicionado com sucesso"


@apiRouter.get("/decks")
def get_decks():
    return view_decks()

@apiRouter.get("/cards")
def get_collection(filter:str = "all"):
    return view_colection(filter)


class CardToDeckRequest(BaseModel):
    deck_name: str
    card_name: str
    quantity: int

@apiRouter.post("/decks/cards")
def insert_card_to_deck(info: CardToDeckRequest):
    add_card_to_deck(
        info.deck_name, 
        info.card_name, 
        info.quantity
        )
    return "Carta adicionada ao deck"

@apiRouter.get("/deck/cards/{deck}")
def get_decklist(deck: str):
    return show_decklist(deck)

@apiRouter.get("/status")
def status():
    server_data = {"status": "StB API online", "version": "1.0"}

    return server_data


