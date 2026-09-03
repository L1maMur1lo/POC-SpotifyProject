from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class Item_Queue(BaseModel):
    track_uri: str
    ms_played: int
    ts: datetime
    offline: Optional[bool] = False
    offline_ts: Optional[int] = 0
    source_file: str
    source_file_row: int

    # Transformando dados
    @field_validator('track_uri', mode='before')
    @classmethod
    def extract_track_id(cls, value: str) -> str:
        """Extrai apenas o id do dado bruto"""
        if isinstance(value, str) and ':' in value:
            return value.rsplit(':', maxsplit=1)[-1]
        return value

    @field_validator('offline', mode='before')
    @classmethod
    def only_boolean(cls, value) -> bool:
        """Transforma valores nulos em boolean"""
        if not type(value) is bool:
            value = False
            return value
        return value