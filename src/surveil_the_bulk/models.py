from pydantic import BaseModel, Field, ConfigDict, computed_field, AliasPath, model_validator, field_validator
from typing import Optional


class CardFace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name:str
    produced_mana: Optional[list[str]] = None
    power: Optional[str] = None
    toughness: Optional[str] = None
    mana_cost:str
    type_line:str
    oracle_text:str
    image_url:str  = Field(alias=AliasPath('image_uris','normal'))



class MTGCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id:str
    set:str
    collector_number:str
    color_identity:list[str] = Field(default_factory=list)
    price_usd:Optional[float] = Field(default=0.0,alias=AliasPath('prices','usd'))
    price_usd_foil:Optional[float] = Field(default=0.0,alias=AliasPath('prices','usd_foil'))
    legalities:list[str] = Field(default_factory=list)
    cmc:int
    card_faces: list[CardFace] = Field(default_factory=list)
    
    @model_validator(mode="before")
    @classmethod
    def validate_card_faces(cls, data: dict)-> dict:
        if 'card_faces' not in data:
            data["card_faces"] = [{
                'name': data.pop("name"),
                'produced_mana': data.pop("produced_mana",None),
                'power': data.pop("power",None),
                'toughness': data.pop("toughness",None),
                'mana_cost': data.pop('mana_cost'),
                'type_line': data.pop('type_line'),
                'oracle_text': data.pop('oracle_text'),
                'image_uris': data.pop('image_uris')
            }]
        return data

    @field_validator("legalities",mode="before")
    @classmethod
    def legal_list(cls, v):
        if isinstance(v, dict):
            return [
                format for format, legality in v.items() if legality == 'legal'
            ]
        return v






