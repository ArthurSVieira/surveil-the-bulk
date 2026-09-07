from pydantic import BaseModel, Field, ConfigDict, AliasPath, model_validator, field_validator
from typing import Optional


class CardFace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str
    power: Optional[str] = None
    toughness: Optional[str] = None
    mana_cost: str
    type_line: str
    oracle_text: str
    image_url: str = Field(alias=AliasPath('image_uris', 'normal'))
class MTGCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    set_code: str = Field(alias="set")
    collector_number: str
    cmc: float  
    

    color_identity: list[str] = Field(default_factory=list)
    produced_mana: list[str] = Field(default_factory=list)
    legalities: list[str] = Field(default_factory=list)
    
 
    price_usd: Optional[float] = Field(default=None, alias=AliasPath('prices', 'usd'))
    price_usd_foil: Optional[float] = Field(default=None, alias=AliasPath('prices', 'usd_foil'))
    

    card_faces: list[CardFace] = Field(default_factory=list)
    
    @model_validator(mode="before")
    @classmethod
    def build_card_faces(cls, data: dict) -> dict:
        if 'card_faces' not in data:
            data['card_faces'] = [{
                'name': data.get("name"),
                'power': data.get("power"),
                'toughness': data.get("toughness"),
                'mana_cost': data.get("mana_cost", ""),
                'type_line': data.get("type_line", ""),
                'oracle_text': data.get("oracle_text", ""),
                'image_uris': data.get("image_uris", {}) 
            }]
        return data
    @field_validator("legalities", mode="before")
    @classmethod
    def filter_legal_formats(cls, v):
        if isinstance(v, dict):
            return [fmt for fmt, legality in v.items() if legality == 'legal']
        return v

