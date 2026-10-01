from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from xdraco_scanner import inspect_nft


app = FastAPI(
    title="MIR4 NFT Scanner",
    version="1.0.0"
)


# =========================================================
# CONFIGURAÇÃO PRINCIPAL
# =========================================================

MAX_POWER = 500_000
MIN_EVA = 5_000

# PERSONAGEM DE REFERÊNCIA
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


# =========================================================
# CALCULAR SEMELHANÇA
# =========================================================

def similarity(value, target):

    if target <= 0:
        return 0

    return min(
        (value / target) * 100,
        100
    )


# =========================================================
# CALCULAR NOTA DO PERSONAGEM
# =========================================================

def calculate_score(character: NFTCharacter):

    # NUNCA ACEITAR ACIMA DE 500 MIL POWER
    if character.power > MAX_POWER:
        return 0

    # EVA PRECISA SER 5.000 OU MAIS
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

    # EVA É A PRIORIDADE MÁXIMA
    final_score = (
        eva_score * 0.40
        + crit_eva_score * 0.25
        + skill_score * 0.15
        + pvp_score * 0.12
        + all_reduction_score * 0.08
    )

    return round(final_score, 2)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.get("/")
def home():

    return {

        "status": "online",

        "robot":
            "MIR4 NFT Scanner",

        "class":
            "Arbalista",

        "max_power":
            MAX_POWER,

        "minimum_evasion":
            MIN_EVA,

        "priority": [
            "EVA",
            "CRIT EVA",
            "Skill DMG Reduction",
            "PvP DMG Reduction",
            "All DMG Reduction"
        ],

        "objective":
            "Encontrar Arbalista EVA + TANK + DANO"
    }


# =========================================================
# ANALISAR PERSONAGEM MANUALMENTE
# =========================================================

@app.post("/analyze")
def analyze(character: NFTCharacter):

    character_class = (
        character.character_class.lower()
    )

    # SOMENTE ARBALISTA
    if character_class not in [
        "arbalist",
        "arbalista"
    ]:

        return {
            "approved": False,
            "reason":
                "Classe diferente de Arbalista"
        }

    # POWER NO MÁXIMO 500 MIL
    if character.power > MAX_POWER:

        return {
            "approved": False,
            "reason":
                "Power acima de 500.000"
        }

    # EVA MÍNIMA 5 MIL
    if character.eva < MIN_EVA:

        return {
            "approved": False,
            "reason":
                "EVA abaixo de 5.000"
        }

    score = calculate_score(character)

    return {

        "approved": True,

        "name":
            character.name,

        "nft_id":
            character.nft_id,

        "power":
            character.power,

        "best_deck":
            character.best_deck,

        "eva":
            character.eva,

        "crit_eva":
            character.crit_eva,

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


# =========================================================
# ESCANEAR NFT REAL DO XDRACO
# =========================================================

@app.get("/scan/{trade_id}")
async def scan_nft(trade_id: str):

    try:

        result = await inspect_nft(
            trade_id
        )

        return {

            "scanner":
                "MIR4 NFT Scanner",

            "result":
                result
        }

    except Exception as error:

        return {

            "scanner":
                "MIR4 NFT Scanner",

            "error":
                str(error)
        }
