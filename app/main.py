"""Punto de entrada de la aplicación web FastAPI para FlashArcade."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.repository import GameNotFoundError, GameRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

app = FastAPI(title="FlashArcade Portal", version="1.0.0")
repo = GameRepository()

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    logger.warning("Directorio estático no encontrado en '%s'.", STATIC_DIR)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    category: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    """Renderiza el catálogo principal con filtros opcionales de categoría y búsqueda.

    Args:
        request: Petición HTTP entrante de Starlette/FastAPI.
        category: Categoría seleccionada para filtrar el catálogo.
        q: Término de búsqueda textual.

    Returns:
        Respuesta HTML con la plantilla `index.html`.
    """
    games = repo.get_all(category=category, query=q)
    categories = repo.get_categories()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "games": games,
            "categories": categories,
            "selected_category": category or "",
            "query": q or "",
        },
    )


@app.get("/play/{slug}", response_class=HTMLResponse)
def play_game(request: Request, slug: str) -> HTMLResponse:
    """Renderiza el reproductor Ruffle para el juego indicado por `slug`.

    Args:
        request: Petición HTTP entrante de Starlette/FastAPI.
        slug: Identificador del juego en la URL.

    Returns:
        Respuesta HTML con la plantilla `play.html`.

    Raises:
        HTTPException: Si el `slug` está vacío o no corresponde a un juego existente.
    """
    normalized_slug = slug.strip()
    if not normalized_slug:
        raise HTTPException(status_code=404, detail="Slug de juego no válido.")

    try:
        updated_game = repo.increment_plays(normalized_slug)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return templates.TemplateResponse(
        request=request,
        name="play.html",
        context={"game": updated_game},
    )