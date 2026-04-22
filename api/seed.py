# backend/seed.py
import httpx
import asyncio
import logging
from sqlalchemy.orm import Session
from models import (
    Pokemon, Type, Ability, EggGroup, Move,
    TypeEffectiveness, pokemon_types, pokemon_abilities,
    pokemon_egg_groups, pokemon_moves_table
)
from database import engine, Base, SessionLocal

logger = logging.getLogger(__name__)

POKEAPI_BASE = "https://pokeapi.co/api/v2"
MAX_POKEMON = 898  # Первые 8 поколений (можно уменьшить для тестов)
BATCH_SIZE = 20


async def fetch_json(client: httpx.AsyncClient, url: str, retries=3) -> dict | None:
    """Получение JSON с повторными попытками."""
    for attempt in range(retries):
        try:
            resp = await client.get(url, timeout=30.0)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 404:
                return None
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            await asyncio.sleep(2 ** attempt)
    return None


async def seed_types(client: httpx.AsyncClient, db: Session):
    """Загрузка типов и таблицы эффективности."""
    logger.info("Seeding types...")
    data = await fetch_json(client, f"{POKEAPI_BASE}/type?limit=30")
    if not data:
        return

    type_map = {}
    for item in data["results"]:
        type_data = await fetch_json(client, item["url"])
        if not type_data or type_data["id"] > 10000:
            continue
        
        db_type = Type(id=type_data["id"], name=type_data["name"])
        db.merge(db_type)
        type_map[type_data["name"]] = type_data
    
    db.commit()
    logger.info(f"Loaded {len(type_map)} types")

    # Таблица эффективности типов
    logger.info("Seeding type effectiveness...")
    all_types = db.query(Type).all()
    type_id_map = {t.name: t.id for t in all_types}

    for type_name, type_data in type_map.items():
        atk_id = type_id_map.get(type_name)
        if not atk_id:
            continue

        damage_relations = type_data.get("damage_relations", {})

        # double_damage_to → 2x
        for t in damage_relations.get("double_damage_to", []):
            def_id = type_id_map.get(t["name"])
            if def_id:
                db.merge(TypeEffectiveness(
                    attacking_type_id=atk_id,
                    defending_type_id=def_id,
                    multiplier=2.0,
                    id=atk_id * 100 + def_id  # детерминированный ID
                ))

        # half_damage_to → 0.5x
        for t in damage_relations.get("half_damage_to", []):
            def_id = type_id_map.get(t["name"])
            if def_id:
                db.merge(TypeEffectiveness(
                    attacking_type_id=atk_id,
                    defending_type_id=def_id,
                    multiplier=0.5,
                    id=atk_id * 100 + def_id
                ))

        # no_damage_to → 0x
        for t in damage_relations.get("no_damage_to", []):
            def_id = type_id_map.get(t["name"])
            if def_id:
                db.merge(TypeEffectiveness(
                    attacking_type_id=atk_id,
                    defending_type_id=def_id,
                    multiplier=0.0,
                    id=atk_id * 100 + def_id
                ))

    db.commit()
    logger.info("Type effectiveness loaded")


async def seed_abilities(client: httpx.AsyncClient, db: Session):
    """Загрузка способностей."""
    logger.info("Seeding abilities...")
    offset = 0
    count = 0
    while True:
        data = await fetch_json(client, f"{POKEAPI_BASE}/ability?limit=100&offset={offset}")
        if not data or not data["results"]:
            break
        
        for item in data["results"]:
            ability_data = await fetch_json(client, item["url"])
            if not ability_data:
                continue
            
            # Ищем английское описание
            effect = ""
            short_effect = ""
            for entry in ability_data.get("effect_entries", []):
                if entry["language"]["name"] == "en":
                    effect = entry.get("effect", "")
                    short_effect = entry.get("short_effect", "")
                    break
            
            db.merge(Ability(
                id=ability_data["id"],
                name=ability_data["name"],
                effect=effect,
                short_effect=short_effect
            ))
            count += 1
        
        db.commit()
        if not data.get("next"):
            break
        offset += 100
    
    logger.info(f"Loaded {count} abilities")


async def seed_egg_groups(client: httpx.AsyncClient, db: Session):
    """Загрузка групп яиц."""
    logger.info("Seeding egg groups...")
    data = await fetch_json(client, f"{POKEAPI_BASE}/egg-group?limit=20")
    if not data:
        return
    
    for item in data["results"]:
        eg_data = await fetch_json(client, item["url"])
        if eg_data:
            db.merge(EggGroup(id=eg_data["id"], name=eg_data["name"]))
    
    db.commit()
    logger.info(f"Loaded {len(data['results'])} egg groups")


async def seed_moves(client: httpx.AsyncClient, db: Session):
    """Загрузка приёмов (moves)."""
    logger.info("Seeding moves...")
    all_types = db.query(Type).all()
    type_id_map = {t.name: t.id for t in all_types}
    
    offset = 0
    count = 0
    while True:
        data = await fetch_json(client, f"{POKEAPI_BASE}/move?limit=100&offset={offset}")
        if not data or not data["results"]:
            break
        
        for item in data["results"]:
            move_data = await fetch_json(client, item["url"])
            if not move_data:
                continue
            
            effect = ""
            for entry in move_data.get("effect_entries", []):
                if entry["language"]["name"] == "en":
                    effect = entry.get("short_effect", "")
                    break
            
            type_id = type_id_map.get(
                move_data["type"]["name"]
            ) if move_data.get("type") else None
            
            db.merge(Move(
                id=move_data["id"],
                name=move_data["name"],
                power=move_data.get("power"),
                accuracy=move_data.get("accuracy"),
                pp=move_data.get("pp"),
                type_id=type_id,
                damage_class=move_data.get("damage_class", {}).get("name") if move_data.get("damage_class") else None,
                effect=effect
            ))
            count += 1
        
        db.commit()
        if not data.get("next"):
            break
        offset += 100
    
    logger.info(f"Loaded {count} moves")


async def seed_pokemon_batch(
    client: httpx.AsyncClient,
    db: Session,
    pokemon_ids: list[int],
    species_cache: dict,
    type_id_map: dict,
    ability_id_set: set,
    egg_group_id_map: dict
):
    """Загрузка батча покемонов."""
    tasks_pokemon = [
        fetch_json(client, f"{POKEAPI_BASE}/pokemon/{pid}")
        for pid in pokemon_ids
    ]
    tasks_species = [
        fetch_json(client, f"{POKEAPI_BASE}/pokemon-species/{pid}")
        for pid in pokemon_ids
    ]
    
    pokemon_results = await asyncio.gather(*tasks_pokemon)
    species_results = await asyncio.gather(*tasks_species)
    
    for poke_data, spec_data in zip(pokemon_results, species_results):
        if not poke_data:
            continue
        
        # Парсинг статов
        stats = {}
        for stat in poke_data.get("stats", []):
            stat_name = stat["stat"]["name"]
            stats[stat_name] = stat["base_stat"]
        
        hp = stats.get("hp", 0)
        attack = stats.get("attack", 0)
        defense = stats.get("defense", 0)
        sp_attack = stats.get("special-attack", 0)
        sp_defense = stats.get("special-defense", 0)
        speed = stats.get("speed", 0)
        stat_total = hp + attack + defense + sp_attack + sp_defense + speed
        
        # Спрайты
        sprites = poke_data.get("sprites", {})
        sprite_url = sprites.get("front_default")
        sprite_official = (
            sprites.get("other", {})
            .get("official-artwork", {})
            .get("front_default")
        )
        
        # Данные из species
        generation = None
        is_legendary = False
        is_mythical = False
        is_baby = False
        habitat = None
        color = None
        shape = None
        growth_rate = None
        capture_rate = None
        base_happiness = None
        gender_rate = None
        
        if spec_data:
            gen_url = spec_data.get("generation", {}).get("url", "")
            if gen_url:
                # Извлекаем номер поколения из URL
                generation = int(gen_url.rstrip("/").split("/")[-1])
            
            is_legendary = spec_data.get("is_legendary", False)
            is_mythical = spec_data.get("is_mythical", False)
            is_baby = spec_data.get("is_baby", False)
            habitat = spec_data.get("habitat", {}).get("name") if spec_data.get("habitat") else None
            color = spec_data.get("color", {}).get("name") if spec_data.get("color") else None
            shape = spec_data.get("shape", {}).get("name") if spec_data.get("shape") else None
            growth_rate = spec_data.get("growth_rate", {}).get("name") if spec_data.get("growth_rate") else None
            capture_rate = spec_data.get("capture_rate")
            base_happiness = spec_data.get("base_happiness")
            gender_rate = spec_data.get("gender_rate")
        
        pokemon = Pokemon(
            id=poke_data["id"],
            name=poke_data["name"],
            height=poke_data.get("height"),
            weight=poke_data.get("weight"),
            base_experience=poke_data.get("base_experience"),
            hp=hp, attack=attack, defense=defense,
            sp_attack=sp_attack, sp_defense=sp_defense, speed=speed,
            stat_total=stat_total,
            sprite_url=sprite_url,
            sprite_official=sprite_official,
            generation=generation,
            is_legendary=is_legendary,
            is_mythical=is_mythical,
            is_baby=is_baby,
            habitat=habitat, color=color, shape=shape,
            growth_rate=growth_rate,
            capture_rate=capture_rate,
            base_happiness=base_happiness,
            gender_rate=gender_rate,
        )
        db.merge(pokemon)
        db.flush()
        
        # Типы
        for type_info in poke_data.get("types", []):
            type_name = type_info["type"]["name"]
            tid = type_id_map.get(type_name)
            if tid:
                stmt = pokemon_types.insert().prefix_with("OR IGNORE").values(
                    pokemon_id=poke_data["id"],
                    type_id=tid,
                    slot=type_info["slot"]
                )
                db.execute(stmt)
        
        # Способности
        for ab_info in poke_data.get("abilities", []):
            ab_url = ab_info["ability"]["url"]
            ab_id = int(ab_url.rstrip("/").split("/")[-1])
            if ab_id in ability_id_set:
                stmt = pokemon_abilities.insert().prefix_with("OR IGNORE").values(
                    pokemon_id=poke_data["id"],
                    ability_id=ab_id,
                    is_hidden=ab_info.get("is_hidden", False),
                    slot=ab_info["slot"]
                )
                db.execute(stmt)
        
        # Группы яиц из species
        if spec_data:
            for eg_info in spec_data.get("egg_groups", []):
                eg_name = eg_info["name"]
                eg_id = egg_group_id_map.get(eg_name)
                if eg_id:
                    stmt = pokemon_egg_groups.insert().prefix_with("OR IGNORE").values(
                        pokemon_id=poke_data["id"],
                        egg_group_id=eg_id
                    )
                    db.execute(stmt)
    
    db.commit()


async def seed_all(max_pokemon: int = MAX_POKEMON):
    """Главная функция загрузки всех данных."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        ) as client:
            # 1. Загружаем справочники
            await seed_types(client, db)
            await seed_abilities(client, db)
            await seed_egg_groups(client, db)
            # await seed_moves(client, db)  # Раскомментировать при необходимости (долго)
            
            # 2. Подготовка маппингов
            all_types = db.query(Type).all()
            type_id_map = {t.name: t.id for t in all_types}
            
            all_abilities = db.query(Ability).all()
            ability_id_set = {a.id for a in all_abilities}
            
            all_egg_groups = db.query(EggGroup).all()
            egg_group_id_map = {eg.name: eg.id for eg in all_egg_groups}
            
            # 3. Загружаем покемонов батчами
            logger.info(f"Seeding {max_pokemon} pokemon...")
            for start in range(1, max_pokemon + 1, BATCH_SIZE):
                end = min(start + BATCH_SIZE, max_pokemon + 1)
                batch_ids = list(range(start, end))
                
                await seed_pokemon_batch(
                    client, db, batch_ids, {},
                    type_id_map, ability_id_set, egg_group_id_map
                )
                logger.info(f"  Loaded pokemon {start}-{end-1}")
            
            logger.info("Seeding complete!")
    
    finally:
        db.close()