import re
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional


BASE_URL = "https://www.xdraco.com"

MAX_POWER = 500_000
TARGET_CLASS = "Arbalist"


@dataclass
class NFTBasicInfo:
    trade_id: str
    name: str
    character_class: str
    level: int
    power: int
    server: str
    nft_id: Optional[str]
    url: str


def number(text: str) -> int:
    """Converte 440,466 -> 440466."""
    return int(re.sub(r"[^\d]", "", text))


async def download_nft_page(trade_id: str) -> str:

    url = f"{BASE_URL}/nft/trade/{trade_id}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/140 Safari/537.36"
        )
    }

    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=30
    ) as client:

        response = await client.get(url)
        response.raise_for_status()

        return response.text


def parse_basic_info(
    trade_id: str,
    html: str
) -> Optional[NFTBasicInfo]:

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(" ", strip=True)

    power_match = re.search(
        r"Power\s*Score\s*([\d,]+)",
        text,
        re.I
    )

    level_match = re.search(
        r"Level\s*(\d+)",
        text,
        re.I
    )

    nft_match = re.search(
        r"NFT\s*ID\s*(\d+)",
        text,
        re.I
    )

    if not power_match:
        return None

    power = number(power_match.group(1))

    # REGRA PRINCIPAL
    if power > MAX_POWER:
        return None

    character_class = ""

    classes = [
        "Arbalist",
        "Warrior",
        "Sorcerer",
        "Taoist",
        "Lancer",
        "Darkist",
        "Arcanist",
        "Lionheart"
    ]

    for cls in classes:
        if re.search(
            rf"\b{re.escape(cls)}\b",
            text,
            re.I
        ):
            character_class = cls
            break

    # SOMENTE ARBALISTA
    if character_class.lower() != TARGET_CLASS.lower():
        return None

    server_match = re.search(
        r"\b(?:ASIA|SA|EU|NA)\d{3}\b",
        text,
        re.I
    )

    server = (
        server_match.group(0)
        if server_match
        else "Desconhecido"
    )

    level = (
        int(level_match.group(1))
        if level_match
        else 0
    )

    nft_id = (
        nft_match.group(1)
        if nft_match
        else None
    )

    # Nome será melhorado quando mapearmos
    # os dados estruturados do site.
    name = "Arbalista"

    return NFTBasicInfo(
        trade_id=str(trade_id),
        name=name,
        character_class=character_class,
        level=level,
        power=power,
        server=server,
        nft_id=nft_id,
        url=f"{BASE_URL}/nft/trade/{trade_id}"
    )


async def inspect_nft(trade_id: str):

    html = await download_nft_page(trade_id)

    character = parse_basic_info(
        trade_id,
        html
    )

    if not character:

        return {
            "approved_basic_filter": False,
            "trade_id": trade_id
        }

    return {
        "approved_basic_filter": True,

        "trade_id":
            character.trade_id,

        "class":
            character.character_class,

        "level":
            character.level,

        "power":
            character.power,

        "server":
            character.server,

        "nft_id":
            character.nft_id,

        # LINK DIRETO QUE VOCÊ PEDIU
        "xdraco_url":
            character.url,

        "next_analysis": {
            "stat": True,
            "spirit_decks": "1-10",
            "magic_stones": True,
            "mystical_piece_decks": "1-10",
            "eva": True,
            "crit_eva": True,
            "damage_reductions": True
        }
    }
