"""Repositorio en memoria para el catálogo de juegos Flash y sus métricas de uso."""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from enum import Enum
from threading import Lock

logger = logging.getLogger(__name__)


class GameNotFoundError(LookupError):
    """Se lanza cuando no existe un juego con el identificador o slug solicitado."""


class GameEngine(str, Enum):
    """Motores de emulación soportados por el portal."""

    RUFFLE = "ruffle"


@dataclass(frozen=True)
class Game:
    """Representa la metadata, el motor y el contador de partidas de un juego."""

    slug: str
    title: str
    swf_filename: str
    category: str
    description: str
    engine: GameEngine = GameEngine.RUFFLE
    plays: int = 0

    @property
    def swf_url(self) -> str:
        """Devuelve la URL pública del archivo `.swf` servida por FastAPI."""
        return f"/static/games/{self.swf_filename}"


@dataclass(frozen=True)
class _GameSeed:
    """Definición inicial inmutable de un juego antes de instanciar `Game`."""

    slug: str
    title: str
    swf_filename: str
    category: str
    description: str
    engine: GameEngine = GameEngine.RUFFLE


_CATALOG_SEEDS: tuple[_GameSeed, ...] = (
    _GameSeed(
        slug="bob-the-robber",
        title="Bob the Robber",
        swf_filename="bobtherobber.swf",
        category="Sigilo y Puzles",
        description="Infíltrate en edificios vigilados, desactiva sistemas de seguridad y escapa sin ser visto.",
    ),
    _GameSeed(
        slug="cactus-mccoy",
        title="Cactus McCoy",
        swf_filename="cactusmccoy.swf",
        category="Acción y Plataformas",
        description="Aventura del lejano oeste con combate cuerpo a cuerpo, armas improvisadas y saltos.",
    ),
    _GameSeed(
        slug="cactus-mccoy-2",
        title="Cactus McCoy 2",
        swf_filename="cactusmccoy2.swf",
        category="Acción y Plataformas",
        description="Secuela de acción lateral con nuevas ubicaciones, enemigos y mejoras de combate.",
    ),
    _GameSeed(
        slug="earn-to-die",
        title="Earn to Die",
        swf_filename="earntodie.swf",
        category="Conducción y Zombis",
        description="Mejora tu vehículo y ábrete paso a toda velocidad entre hordas de zombis en el desierto.",
    ),
    _GameSeed(
        slug="earn-to-die-2",
        title="Earn to Die 2",
        swf_filename="earntodie2.swf",
        category="Conducción y Zombis",
        description="Rutas con múltiples niveles, nuevos vehículos y mayor destrucción en un apocalipsis zombi.",
    ),
    _GameSeed(
        slug="fancy-pants-adventure",
        title="Fancy Pants Adventure",
        swf_filename="fancypantsadventure.swf",
        category="Plataformas",
        description="Plataformas de ritmo rápido con física fluida, acrobacias y niveles dibujados a mano.",
    ),
    _GameSeed(
        slug="hobo",
        title="Hobo",
        swf_filename="hobo.swf",
        category="Beat 'em up",
        description="Combate callejero clásico con combos y movimientos especiales en escenarios urbanos.",
    ),
    _GameSeed(
        slug="jacksmith",
        title="Jacksmith",
        swf_filename="jacksmith.swf",
        category="Estrategia y Gestión",
        description="Forja armas en tu taller para equipar a tu equipo y acompáñalos en las batallas.",
    ),
    _GameSeed(
        slug="papa-louie",
        title="Papa Louie",
        swf_filename="papalouie.swf",
        category="Acción y Plataformas",
        description="Rescata a los clientes atrapados en mundos dulces saltando y derrotando enemigos.",
    ),
    _GameSeed(
        slug="papas-freezeria",
        title="Papa's Freezeria",
        swf_filename="papasfreezeria_v2.swf",
        category="Estrategia y Gestión",
        description="Prepara helados sundae personalizados bajo presión para satisfacer a cada cliente.",
    ),
    _GameSeed(
        slug="raft-wars",
        title="Raft Wars",
        swf_filename="raftwars.swf",
        category="Artillería y Puzles",
        description="Calcula ángulos y potencia para lanzar proyectiles y defender tu balsa.",
    ),
    _GameSeed(
        slug="sift-heads",
        title="Sift Heads",
        swf_filename="siftheads.swf",
        category="Acción y Shooter",
        description="Primera entrega de acción estilizada con misiones y tiroteos.",
    ),
    _GameSeed(
        slug="sift-heads-2",
        title="Sift Heads 2",
        swf_filename="siftheads2.swf",
        category="Acción y Shooter",
        description="Continúa la historia con nuevas misiones, personajes y arsenal.",
    ),
    _GameSeed(
        slug="sift-heads-3",
        title="Sift Heads 3",
        swf_filename="siftheads3.swf",
        category="Acción y Shooter",
        description="Tercera entrega con mayor variedad de escenarios y enfrentamientos.",
    ),
    _GameSeed(
        slug="sift-heads-4",
        title="Sift Heads 4",
        swf_filename="siftheads4.swf",
        category="Acción y Shooter",
        description="Cuarta entrega de la saga con nuevas secuencias de acción y progresión.",
    ),
    _GameSeed(
        slug="sift-heads-5",
        title="Sift Heads 5",
        swf_filename="siftheads5.swf",
        category="Acción y Shooter",
        description="Quinta entrega de la serie manteniendo el estilo de acción y aventura.",
    ),
    _GameSeed(
        slug="super-smash-flash",
        title="Super Smash Flash",
        swf_filename="supersmashflash.swf",
        category="Lucha",
        description="Combates de arena estilo crossover con personajes icónicos y modos multijugador local.",
    ),
    _GameSeed(
        slug="tequila-zombies-2",
        title="Tequila Zombies 2",
        swf_filename="tequila_zombies_2.swf",
        category="Acción y Shooter",
        description="Enfréntate a oleadas de zombis con distintas armas y escenarios llenos de acción.",
    ),
    _GameSeed(
        slug="zombie-alien-parasites",
        title="Zombie Alien Parasites",
        swf_filename="zombiealienparasites.swf",
        category="Acción y Plataformas",
        description="Combate contra criaturas infectadas por parásitos alienígenas en niveles de acción.",
    ),
)


class GameRepository:
    """Gestiona el acceso a los juegos, filtros de catálogo y métricas de partidas."""

    def __init__(self, seeds: tuple[_GameSeed, ...] = _CATALOG_SEEDS) -> None:
        """Inicializa el repositorio en memoria con las semillas del catálogo.

        Args:
            seeds: Tupla de definiciones iniciales de juegos.
        """
        self._lock = Lock()
        self._games: dict[str, Game] = {
            seed.slug: Game(
                slug=seed.slug,
                title=seed.title,
                swf_filename=seed.swf_filename,
                category=seed.category,
                description=seed.description,
                engine=seed.engine,
                plays=0,
            )
            for seed in seeds
        }
        logger.info("GameRepository inicializado con %d juegos.", len(self._games))

    def get_all(
        self,
        category: str | None = None,
        query: str | None = None,
    ) -> list[Game]:
        """Devuelve los juegos filtrados opcionalmente por categoría y texto de búsqueda.

        Args:
            category: Categoría exacta; ignora valores vacíos, ``"all"`` o ``"todas"``.
            query: Texto a buscar en título, categoría o descripción.

        Returns:
            Lista de instancias de `Game` que cumplen los criterios.
        """
        normalized_category = category.strip().lower() if category else ""
        normalized_query = query.strip().lower() if query else ""

        with self._lock:
            games = list(self._games.values())

        if normalized_category and normalized_category not in {"all", "todas"}:
            games = [
                game for game in games if game.category.lower() == normalized_category
            ]

        if normalized_query:
            games = [
                game
                for game in games
                if normalized_query in game.title.lower()
                or normalized_query in game.category.lower()
                or normalized_query in game.description.lower()
            ]

        return games

    def get_categories(self) -> list[str]:
        """Devuelve la lista ordenada de categorías únicas presentes en el catálogo.

        Returns:
            Lista de nombres de categorías.
        """
        with self._lock:
            categories = {game.category for game in self._games.values()}
        return sorted(categories)

    def get_by_slug(self, slug: str) -> Game:
        """Obtiene un juego por su `slug`.

        Args:
            slug: Identificador amigable del juego.

        Returns:
            Instancia de `Game` correspondiente.

        Raises:
            GameNotFoundError: Si no existe un juego con el `slug` dado.
        """
        cleaned_slug = slug.strip()
        with self._lock:
            game = self._games.get(cleaned_slug)
            if game is None:
                logger.warning("Juego no encontrado para slug='%s'.", cleaned_slug)
                raise GameNotFoundError(f"No se encontró el juego '{cleaned_slug}'.")
            return game

    def increment_plays(self, slug: str) -> Game:
        """Incrementa en 1 el contador de partidas de un juego de forma atómica.

        Args:
            slug: Identificador amigable del juego.

        Returns:
            Instancia actualizada de `Game`.

        Raises:
            GameNotFoundError: Si no existe un juego con el `slug` dado.
        """
        cleaned_slug = slug.strip()
        with self._lock:
            current = self._games.get(cleaned_slug)
            if current is None:
                logger.warning(
                    "Intento de incrementar partidas para slug inexistente='%s'.",
                    cleaned_slug,
                )
                raise GameNotFoundError(f"No se encontró el juego '{cleaned_slug}'.")

            updated = replace(current, plays=current.plays + 1)
            self._games[cleaned_slug] = updated
            return updated