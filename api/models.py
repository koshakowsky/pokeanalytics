from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, Table, Text
)
from sqlalchemy.orm import relationship
from database import Base

pokemon_types = Table(
    "pokemon_types", Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id"), primary_key=True),
    Column("type_id", Integer, ForeignKey("types.id"), primary_key=True),
    Column("slot", Integer, nullable=False, default=1),
)

pokemon_abilities = Table(
    "pokemon_abilities", Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id"), primary_key=True),
    Column("ability_id", Integer, ForeignKey("abilities.id"), primary_key=True),
    Column("is_hidden", Boolean, default=False),
    Column("slot", Integer, nullable=False, default=1),
)

pokemon_egg_groups = Table(
    "pokemon_egg_groups", Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id"), primary_key=True),
    Column("egg_group_id", Integer, ForeignKey("egg_groups.id"), primary_key=True),
)

pokemon_moves_table = Table(
    "pokemon_moves", Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("move_id", Integer, ForeignKey("moves.id")),
    Column("learn_method", String(50)),
    Column("level_learned", Integer, default=0),
)


class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    height = Column(Integer)
    weight = Column(Integer)
    base_experience = Column(Integer)

    hp = Column(Integer, nullable=False, default=0)
    attack = Column(Integer, nullable=False, default=0)
    defense = Column(Integer, nullable=False, default=0)
    sp_attack = Column(Integer, nullable=False, default=0)
    sp_defense = Column(Integer, nullable=False, default=0)
    speed = Column(Integer, nullable=False, default=0)
    stat_total = Column(Integer, nullable=False, default=0)
    
    sprite_url = Column(String(500))
    sprite_official = Column(String(500))
    
    generation = Column(Integer, index=True)
    is_legendary = Column(Boolean, default=False)
    is_mythical = Column(Boolean, default=False)
    is_baby = Column(Boolean, default=False)
    habitat = Column(String(50), index=True)
    color = Column(String(30), index=True)
    shape = Column(String(30))
    growth_rate = Column(String(30))
    
    capture_rate = Column(Integer)
    base_happiness = Column(Integer)
    gender_rate = Column(Integer)
    
    types = relationship("Type", secondary=pokemon_types, back_populates="pokemon")
    abilities = relationship("Ability", secondary=pokemon_abilities, back_populates="pokemon")
    egg_groups = relationship("EggGroup", secondary=pokemon_egg_groups, back_populates="pokemon")
    
    @property
    def height_m(self):
        return self.height / 10 if self.height else None
    
    @property
    def weight_kg(self):
        return self.weight / 10 if self.weight else None


class Type(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    
    pokemon = relationship("Pokemon", secondary=pokemon_types, back_populates="types")
    
    attacking_effectiveness = relationship(
        "TypeEffectiveness",
        foreign_keys="TypeEffectiveness.attacking_type_id",
        back_populates="attacking_type"
    )
    defending_effectiveness = relationship(
        "TypeEffectiveness",
        foreign_keys="TypeEffectiveness.defending_type_id",
        back_populates="defending_type"
    )


class Ability(Base):
    __tablename__ = "abilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    effect = Column(Text)
    short_effect = Column(String(500))
    
    pokemon = relationship("Pokemon", secondary=pokemon_abilities, back_populates="abilities")


class EggGroup(Base):
    __tablename__ = "egg_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    pokemon = relationship("Pokemon", secondary=pokemon_egg_groups, back_populates="egg_groups")


class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    power = Column(Integer)
    accuracy = Column(Integer)
    pp = Column(Integer)
    type_id = Column(Integer, ForeignKey("types.id"))
    damage_class = Column(String(20))
    effect = Column(Text)
    
    type = relationship("Type")


class TypeEffectiveness(Base):
    __tablename__ = "type_effectiveness"

    id = Column(Integer, primary_key=True, autoincrement=True)
    attacking_type_id = Column(Integer, ForeignKey("types.id"), nullable=False)
    defending_type_id = Column(Integer, ForeignKey("types.id"), nullable=False)
    multiplier = Column(Float, nullable=False)
    
    attacking_type = relationship("Type", foreign_keys=[attacking_type_id])
    defending_type = relationship("Type", foreign_keys=[defending_type_id])