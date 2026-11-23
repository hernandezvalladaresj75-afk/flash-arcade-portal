"""Módulo de esquemas de validación de datos para el portal de juegos."""

from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class GameCategory(str, Enum):
    """Categorías disponibles en el portal arcade."""

    ACTION = "Acción"
    PUZZLE = "Puzzles"
    ADVENTURE = "Aventura"
    RACING = "Carreras"
    STRATEGY = "Estrategia"


class GameEngine(str, Enum):
    """Motor de ejecución del juego."""

    FLASH_SWF = "swf"
    HTML5_IFRAME = "html5"


class GameSchema(BaseModel):
    """Esquema que representa un videojuego dentro del catálogo."""

    id: str = Field(..., description="Identificador único (slug) del juego")
    title: str = Field(..., min_length=2, max_length=100, description="Título público")
    description: str = Field(..., max_length=500, description="Sinopsis y controles")
    category: GameCategory = Field(..., description="Género principal")
    engine: GameEngine = Field(default=GameEngine.FLASH_SWF, description="Tipo de archivo")
    file_url: str = Field(..., description="Ruta relativa o URL al archivo .swf o HTML5")
    thumbnail_url: str = Field(..., description="URL de la imagen de portada (16:9)")
    plays: int = Field(default=0, ge=0, description="Contador de partidas jugadas")