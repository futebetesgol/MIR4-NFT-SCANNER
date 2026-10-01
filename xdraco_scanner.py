import re
import json
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional


BASE_URL = "https://www.xdraco.com"

# ==========================================================
# REGRAS DO NOSSO SCANNER
# ==========================================================

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


# ==========================================================
# CONVERTER NÚMEROS
# ==========================================================

def number(text: str) -> int:

    if not text:
        return 0

    value = re.sub(
        r"[^\d]",
        "",
        str(text)
    )

    if not value:
        return 0

    return int(value)


# ==========================================================
# BAIXAR PÁGINA DO NFT
# ==========================================================

async def download_nft_page(trade_id: str):

    url = f"{BASE_URL}/nft/trade/{trade_id}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,"
            "image/webp,*/*;q=0.8"
        ),
        "Accept-Language":
            "en-US,en;q=0.9,pt-BR;q=0.8",
        "Cache-Control":
            "no-cache",
        "Pragma":
            "no-cache",
    }

    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=30
    ) as client:

        response = await client.get(url)

        print("")
        print("========== XDRACO HTTP ==========")
        print("URL:", url)
        print("STATUS:", response.status_code)
        print(
            "CONTENT-TYPE:",
            response.headers.get(
                "content-type",
                ""
            )
        )
        print(
            "TAMANHO HTML:",
            len(response.text)
        )
        print(
            "URL FINAL:",
            str(response.url)
        )
        print("=================================")
        print("")

        response.raise_for_status()

        return response.text


# ==========================================================
# PROCURAR DADOS DENTRO DE JSON
# ==========================================================

def walk_json(data, path="root"):

    found = []

    if isinstance(data, dict):

        for key, value in data.items():

            current_path = (
                f"{path}.{key}"
            )

            key_lower = str(key).lower()

            interesting = [
                "power",
                "class",
                "level",
                "server",
                "nft",
                "character",
                "evasion",
                "eva",
                "crit",
                "spirit",
                "stone",
                "mystical",
                "deck",
            ]

            if any(
                word in key_lower
                for word in interesting
            ):

                if isinstance(
                    value,
                    (str, int, float, bool)
                ):

                    found.append(
                        (
                            current_path,
                            value
                        )
                    )

            found.extend(
                walk_json(
                    value,
                    current_path
                )
            )

    elif isinstance(data, list):

        for index, value in enumerate(data):

            found.extend(
                walk_json(
                    value,
                    f"{path}[{index}]"
                )
            )

    return found


# ==========================================================
# DIAGNÓSTICO DO HTML
# ==========================================================

def diagnose_html(
    trade_id: str,
    html: str
):

    print("")
    print(
        "=========================================="
    )
    print(
        "        DIAGNÓSTICO XDRACO"
    )
    print(
        "=========================================="
    )

    lower_html = html.lower()

    keywords = [
        "power",
        "power score",
        "arbalist",
        "character",
        "spirit",
        "magic stone",
        "mystical piece",
        "evasion",
        "crit eva",
        "__next_data__",
        "application/json",
    ]

    print("")
    print("PALAVRAS ENCONTRADAS:")
    print("")

    for keyword in keywords:

        exists = (
            keyword.lower()
            in lower_html
        )

        print(
            f"{keyword}: "
            f"{'SIM' if exists else 'NAO'}"
        )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # ======================================================
    # PROCURAR SCRIPTS JSON
    # ======================================================

    scripts = soup.find_all("script")

    print("")
    print(
        "TOTAL DE <script>:",
        len(scripts)
    )

    json_scripts = []

    for index, script in enumerate(scripts):

        script_type = (
            script.get("type")
            or ""
        ).lower()

        script_id = (
            script.get("id")
            or ""
        )

        content = (
            script.string
            or script.get_text()
            or ""
        ).strip()

        if not content:
            continue

        if (
            "json" in script_type
            or script_id == "__NEXT_DATA__"
        ):

            json_scripts.append(
                (
                    index,
                    script_type,
                    script_id,
                    content
                )
            )

    print(
        "SCRIPTS JSON:",
        len(json_scripts)
    )

    # ======================================================
    # ANALISAR JSON EMBUTIDO
    # ======================================================

    for (
        index,
        script_type,
        script_id,
        content
    ) in json_scripts:

        print("")
        print(
            "------------------------------------------"
        )

        print(
            f"SCRIPT #{index}"
        )

        print(
            "TYPE:",
            script_type
        )

        print(
            "ID:",
            script_id
        )

        print(
            "TAMANHO:",
            len(content)
        )

        try:

            data = json.loads(
                content
            )

            found = walk_json(
                data
            )

            print(
                "CAMPOS INTERESSANTES:",
                len(found)
            )

            # Não imprimir milhares de linhas.
            for path, value in found[:150]:

                print(
                    f"{path} = {value}"
                )

        except Exception as error:

            print(
                "Não foi possível converter "
                "esse script para JSON:",
                str(error)
            )

    # ======================================================
    # MOSTRAR TRECHOS PERTO DE PALAVRAS IMPORTANTES
    # ======================================================

    plain_text = soup.get_text(
        " ",
        strip=True
    )

    print("")
    print(
        "=========================================="
    )
    print(
        "TRECHOS DO TEXTO:"
    )
    print(
        "=========================================="
    )

    search_terms = [
        "Power",
        "Arbalist",
        "Spirit",
        "Magic Stone",
        "Mystical Piece",
        "Evasion",
    ]

    for term in search_terms:

        match = re.search(
            re.escape(term),
            plain_text,
            re.I
        )

        if not match:
            continue

        start = max(
            0,
            match.start() - 200
        )

        end = min(
            len(plain_text),
            match.end() + 500
        )

        print("")
        print(
            f"--- {term} ---"
        )

        print(
            plain_text[start:end]
        )

    print("")
    print(
        "=========================================="
    )
    print(
        "       FIM DO DIAGNÓSTICO"
    )
    print(
        "=========================================="
    )
    print("")


# ==========================================================
# TENTAR PEGAR DADOS BÁSICOS
# ==========================================================

def parse_basic_info(
    trade_id: str,
    html: str
) -> Optional[NFTBasicInfo]:

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    # Primeiro fazemos o diagnóstico.
    diagnose_html(
        trade_id,
        html
    )

    # ======================================================
    # POWER
    # ======================================================

    power_patterns = [
        r"Power\s*Score\s*[:\-]?\s*([\d,]+)",
        r"Power\s*[:\-]?\s*([\d,]+)",
    ]

    power = 0

    for pattern in power_patterns:

        match = re.search(
            pattern,
            text,
            re.I
        )

        if match:

            power = number(
                match.group(1)
            )

            break

    # ======================================================
    # CLASSE
    # ======================================================

    classes = [
        "Arbalist",
        "Warrior",
        "Sorcerer",
        "Taoist",
        "Lancer",
        "Darkist",
        "Arcanist",
        "Lionheart",
    ]

    character_class = ""

    for cls in classes:

        if re.search(
            rf"\b{re.escape(cls)}\b",
            text,
            re.I
        ):

            character_class = cls
            break

    # ======================================================
    # LEVEL
    # ======================================================

    level_match = re.search(
        r"(?:Level|Lv\.?)\s*[:\-]?\s*(\d+)",
        text,
        re.I
    )

    level = (
        int(level_match.group(1))
        if level_match
        else 0
    )

    # ======================================================
    # NFT ID
    # ======================================================

    nft_match = re.search(
        r"NFT\s*ID\s*[:#\-]?\s*(\d+)",
        text,
        re.I
    )

    nft_id = (
        nft_match.group(1)
        if nft_match
        else None
    )

    # ======================================================
    # SERVIDOR
    # ======================================================

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

    print("")
    print(
        "========== RESULTADO BÁSICO =========="
    )
    print(
        "CLASSE:",
        character_class
        or "NÃO ENCONTRADA"
    )
    print(
        "POWER:",
        power
    )
    print(
        "LEVEL:",
        level
    )
    print(
        "NFT ID:",
        nft_id
    )
    print(
        "SERVER:",
        server
    )
    print(
        "======================================"
    )
    print("")

    # ======================================================
    # NÃO INVENTAR RESULTADOS
    # ======================================================

    if not character_class:

        print(
            "FALHA: classe não encontrada."
        )

        return None

    if power <= 0:

        print(
            "FALHA: Power Score não encontrado."
        )

        return None

    # ======================================================
    # REGRAS OBRIGATÓRIAS
    # ======================================================

    if (
        character_class.lower()
        != TARGET_CLASS.lower()
    ):

        print(
            "ELIMINADO: não é Arbalista."
        )

        return None

    if power > MAX_POWER:

        print(
            "ELIMINADO: Power acima de 500.000."
        )

        return None

    return NFTBasicInfo(
        trade_id=str(trade_id),
        name="Arbalista",
        character_class=character_class,
        level=level,
        power=power,
        server=server,
        nft_id=nft_id,
        url=(
            f"{BASE_URL}/nft/trade/"
            f"{trade_id}"
        )
    )


# ==========================================================
# INSPECIONAR NFT
# ==========================================================

async def inspect_nft(
    trade_id: str
):

    html = await download_nft_page(
        trade_id
    )

    character = parse_basic_info(
        trade_id,
        html
    )

    if not character:

        return {
            "approved_basic_filter":
                False,

            "trade_id":
                str(trade_id),

            "xdraco_url":
                (
                    f"{BASE_URL}/nft/trade/"
                    f"{trade_id}"
                ),

            "diagnostic":
                "Verifique o log do GitHub Actions."
        }

    return {

        "approved_basic_filter":
            True,

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

        "xdraco_url":
            character.url,

        "next_analysis": {

            "eva":
                True,

            "crit_eva":
                True,

            "skill_damage_reduction":
                True,

            "pvp_damage_reduction":
                True,

            "all_damage_reduction":
                True,

            "spirit_decks":
                "1-10",

            "magic_stones":
                "1-10",

            "mystical_piece_decks":
                "1-10"
        }
    }
