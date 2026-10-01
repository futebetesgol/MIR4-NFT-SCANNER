from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="MIR4 NFT Scanner",
    version="1.0.0"
)

# =========================================================
# PERFIL QUE ESTAMOS PROCURANDO
# =========================================================

MAX_POWER = 500_000
MIN_EVA = 5_000

# Referência aproximada da build enviada
TARGET_EVA = 6204
TARGET_CRIT_EVA = 4390
TARGET_SKILL_REDUCTION = 423.2
TARGET_PVP_REDUCTION = 273.6
TARGET_ALL_REDUCTION = 164.9


class NFTCharacter(BaseModel):
    nft_id: str
    name: str
    character_class: str

    power: int

    eva: float
    crit_eva: float

    skill_damage_reduction: float = 0
    pvp_damage_reduction: float = 0
    all_damage_reduction: float = 0

    accuracy: float = 0
    physical_attack: float = 0
    crit: float = 0

    best_deck: Optional[int] = None

    xdraco_url: str


def similarity(value, target):
    """
    Compara um atributo com nosso personagem de referência.
    100 = atingiu ou ultrapassou o alvo.
    """
    if target <= 0:
        return 0

    return min((value / target) * 100, 100)


def calculate_score(character: NFTCharacter):

    # REGRA OBRIGATÓRIA
    if character.power > MAX_POWER:
        return 0

    # REGRA OBRIGATÓRIA
    if character.eva < MIN_EVA:
        return 0

    eva_score = similarity(
        character.eva,
        TARGET_EVA
    )

    crit_eva_score = similarity(
        character.crit_eva,
        TARGET_CRIT_EVA
    )

    skill_score = similarity(
        character.skill_damage_reduction,
        TARGET_SKILL_REDUCTION
    )

    pvp_score = similarity(
        character.pvp_damage_reduction,
        TARGET_PVP_REDUCTION
    )

    all_reduction_score = similarity(
        character.all_damage_reduction,
        TARGET_ALL_REDUCTION
    )

    # EVA É A MAIOR PRIORIDADE
    final_score = (
        eva_score * 0.40 +
        crit_eva_score * 0.25 +
        skill_score * 0.15 +
        pvp_score * 0.12 +
        all_reduction_score * 0.08
    )

    return round(final_score, 2)


@app.get("/")
def home():

    return {
        "status": "online",
        "robot": "MIR4 NFT Scanner",
        "class": "Arbalista",
        "max_power": MAX_POWER,
        "minimum_evasion": MIN_EVA,
        "objective": "EVA + CRIT EVA + TANK + DANO"
    }


@app.post("/analyze")
def analyze(character: NFTCharacter):

    # SOMENTE ARBALISTA
    character_class = character.character_class.lower()

    if character_class not in [
        "arbalist",
        "arbalista"
    ]:

        return {
            "approved": False,
            "reason": "Classe diferente de Arbalista"
        }

    # NUNCA ACIMA DE 500K
    if character.power > MAX_POWER:

        return {
            "approved": False,
            "reason": "Power acima de 500.000"
        }

    # EVA PRECISA SER 5000+
    if character.eva < MIN_EVA:

        return {
            "approved": False,
            "reason": "EVA abaixo de 5.000"
        }

    score = calculate_score(character)

    return {
        "approved": True,

        "name": character.name,
        "nft_id": character.nft_id,

        "power": character.power,

        "best_deck": character.best_deck,

        "eva": character.eva,
        "crit_eva": character.crit_eva,

        "skill_damage_reduction":
            character.skill_damage_reduction,

        "pvp_damage_reduction":
            character.pvp_damage_reduction,

        "all_damage_reduction":
            character.all_damage_reduction,

        "compatibility":
            f"{score}%",

        "xdraco_url":
            character.xdraco_url
    }
