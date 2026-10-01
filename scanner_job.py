import asyncio
import json
import sys
import traceback

from playwright.async_api import async_playwright


# ==========================================================
# CONFIGURAÇÃO MIR4 NFT SCANNER
# ==========================================================

TRADE_ID = "2330341"

XDRACO_URL = (
    f"https://www.xdraco.com/nft/trade/{TRADE_ID}"
)

MAX_POWER = 500_000
MIN_EVA = 5_000


# ==========================================================
# DETECTOR XDRACO
# ==========================================================

async def run_detector():

    print("")
    print("=" * 70)
    print("MIR4 NFT SCANNER")
    print("=" * 70)

    print("")
    print("BUSCA DEFINIDA:")
    print("Classe: ARBALISTA")
    print("Power máximo: 500.000")
    print("EVA desejada: 5.000+")
    print("Prioridade #1: EVA")
    print("Prioridade #2: CRIT EVA")
    print("Prioridade #3: Skill DMG Reduction")
    print("Prioridade #4: PvP DMG Reduction")
    print("Prioridade #5: All DMG Reduction")

    print("")
    print("=" * 70)
    print("DETECTOR DE API XDRACO")
    print("=" * 70)

    print("")
    print("NFT:", TRADE_ID)
    print("URL:", XDRACO_URL)
    print("")

    captured = []
    character_summary = None
    character_inventory = None
    character_tradehistory = None

    async with async_playwright() as playwright:

        # ==================================================
        # ABRIR CHROMIUM
        # ==================================================

        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = await browser.new_context(
            viewport={
                "width": 1920,
                "height": 1080,
            },
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            ),
        )

        page = await context.new_page()

        # ==================================================
        # CAPTURAR RESPOSTAS
        # ==================================================

        async def capture_response(response):

            nonlocal character_summary
            nonlocal character_inventory
            nonlocal character_tradehistory

            try:

                request = response.request
                resource_type = request.resource_type
                url = response.url

                content_type = (
                    response.headers.get(
                        "content-type",
                        ""
                    ).lower()
                )

                interesting = (
                    resource_type in ["xhr", "fetch"]
                    or "application/json" in content_type
                    or "text/json" in content_type
                )

                if not interesting:
                    return

                print("")
                print("-" * 70)
                print("RESPOSTA ENCONTRADA")
                print("-" * 70)

                print("STATUS:", response.status)
                print("TIPO:", resource_type)
                print("URL:", url)
                print("CONTENT-TYPE:", content_type)

                # ==========================================
                # LER CORPO DA RESPOSTA
                # ==========================================

                try:
                    body = await response.text()
                except Exception as error:
                    print(
                        "Não foi possível ler o corpo:",
                        str(error)
                    )
                    body = ""

                print("TAMANHO:", len(body))

                parsed_body = None

                if body:

                    try:
                        parsed_body = json.loads(body)

                    except Exception:
                        parsed_body = None

                # ==========================================
                # SALVAR REQUISIÇÃO + CONTEÚDO
                # ==========================================

                item = {
                    "status": response.status,
                    "type": resource_type,
                    "content_type": content_type,
                    "url": url,
                }

                if parsed_body is not None:
                    item["response"] = parsed_body

                elif body:
                    item["response_text"] = body[:20000]

                captured.append(item)

                # ==========================================
                # CHARACTER SUMMARY
                # ==========================================

                if "/nft/character/summary" in url:

                    print("")
                    print("=" * 70)
                    print("CHARACTER SUMMARY ENCONTRADO!")
                    print("=" * 70)

                    character_summary = {
                        "status": response.status,
                        "url": url,
                        "data": (
                            parsed_body
                            if parsed_body is not None
                            else body
                        ),
                    }

                    if parsed_body is not None:

                        print(
                            json.dumps(
                                parsed_body,
                                ensure_ascii=False,
                                indent=2
                            )[:20000]
                        )

                    else:
                        print(body[:20000])

                # ==========================================
                # INVENTÁRIO
                # ==========================================

                if "/nft/character/inven" in url:

                    print("")
                    print("=" * 70)
                    print("INVENTÁRIO ENCONTRADO!")
                    print("=" * 70)

                    character_inventory = {
                        "status": response.status,
                        "url": url,
                        "data": (
                            parsed_body
                            if parsed_body is not None
                            else body
                        ),
                    }

                # ==========================================
                # TRADE HISTORY
                # ==========================================

                if "/nft/character/tradehistory" in url:

                    character_tradehistory = {
                        "status": response.status,
                        "url": url,
                        "data": (
                            parsed_body
                            if parsed_body is not None
                            else body
                        ),
                    }

                # ==========================================
                # DIAGNÓSTICO
                # ==========================================

                if body:

                    body_lower = body.lower()

                    keywords = [
                        "power",
                        "powerscore",
                        "power_score",
                        "character",
                        "arbalist",
                        "spirit",
                        "pet",
                        "stone",
                        "magicstone",
                        "magic_stone",
                        "mystical",
                        "deck",
                        "evasion",
                        "eva",
                        "crit",
                        "nft",
                        "trade",
                        "constitution",
                        "potential",
                        "conquest",
                        "codex",
                    ]

                    found = []

                    for keyword in keywords:

                        if keyword in body_lower:
                            found.append(keyword)

                    if found:

                        print("")
                        print(
                            ">>> POSSÍVEL API IMPORTANTE <<<"
                        )

                        print(
                            "PALAVRAS:",
                            ", ".join(found)
                        )

                        print("")
                        print("AMOSTRA DA RESPOSTA:")

                        preview = (
                            body[:5000]
                            .replace("\n", " ")
                            .replace("\r", " ")
                        )

                        print(preview)

            except Exception as error:

                print(
                    "ERRO AO ANALISAR RESPOSTA:",
                    str(error)
                )

        # ==================================================
        # ATIVAR CAPTURA
        # ==================================================

        page.on(
            "response",
            capture_response
        )

        # ==================================================
        # ABRIR NFT
        # ==================================================

        print("")
        print("Abrindo página do NFT...")
        print("")

        try:

            response = await page.goto(
                XDRACO_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            if response:

                print(
                    "STATUS DA PÁGINA:",
                    response.status
                )

        except Exception as error:

            print(
                "AVISO AO ABRIR PÁGINA:",
                str(error)
            )

        # ==================================================
        # ESPERAR JAVASCRIPT
        # ==================================================

        print("")
        print(
            "Esperando JavaScript e APIs..."
        )

        await page.wait_for_timeout(20000)

        # ==================================================
        # PÁGINA RENDERIZADA
        # ==================================================

        print("")
        print("=" * 70)
        print("PÁGINA RENDERIZADA")
        print("=" * 70)

        print(
            "URL FINAL:",
            page.url
        )

        try:
            title = await page.title()
        except Exception:
            title = ""

        print(
            "TÍTULO:",
            title
        )

        try:

            body_text = await page.locator(
                "body"
            ).inner_text(
                timeout=10000
            )

        except Exception:
            body_text = ""

        print(
            "TAMANHO DO TEXTO:",
            len(body_text)
        )

        # ==================================================
        # ORGANIZAR REQUISIÇÕES
        # ==================================================

        unique = {}

        for item in captured:
            unique[item["url"]] = item

        print("")
        print("=" * 70)
        print("REQUISIÇÕES XHR / FETCH / JSON")
        print("=" * 70)

        print(
            "TOTAL:",
            len(unique)
        )

        for index, item in enumerate(
            unique.values(),
            start=1
        ):

            print("")
            print(
                f"REQUISIÇÃO #{index}"
            )

            print(
                "STATUS:",
                item["status"]
            )

            print(
                "TIPO:",
                item["type"]
            )

            print(
                "URL:",
                item["url"]
            )

            if "response" in item:

                print(
                    "CONTEÚDO JSON: SIM"
                )

            else:

                print(
                    "CONTEÚDO JSON: NÃO"
                )

        # ==================================================
        # SALVAR XDRACO_REQUESTS.JSON
        # ==================================================

        output = {

            "trade_id": TRADE_ID,

            "xdraco_url": XDRACO_URL,

            "rules": {

                "class": "Arbalista",

                "max_power": MAX_POWER,

                "minimum_eva": MIN_EVA,

                "priority": [
                    "EVA",
                    "CRIT EVA",
                    "Skill DMG Reduction",
                    "PvP DMG Reduction",
                    "All DMG Reduction",
                ],
            },

            "requests": list(
                unique.values()
            ),
        }

        with open(
            "xdraco_requests.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print("")
        print(
            "ARQUIVO CRIADO: xdraco_requests.json"
        )

        # ==================================================
        # SALVAR CHARACTER SUMMARY
        # ==================================================

        if character_summary is not None:

            with open(
                "character_summary.json",
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    character_summary,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            print("")
            print("=" * 70)
            print("SUCESSO!")
            print("character_summary.json CRIADO")
            print("=" * 70)

        else:

            print("")
            print("=" * 70)
            print("ATENÇÃO!")
            print(
                "character/summary não foi capturado."
            )
            print("=" * 70)

        # ==================================================
        # SALVAR INVENTÁRIO
        # ==================================================

        if character_inventory is not None:

            with open(
                "character_inventory.json",
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    character_inventory,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            print(
                "character_inventory.json CRIADO"
            )

        # ==================================================
        # SALVAR TRADE HISTORY
        # ==================================================

        if character_tradehistory is not None:

            with open(
                "character_tradehistory.json",
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    character_tradehistory,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            print(
                "character_tradehistory.json CRIADO"
            )

        print("")
        print("=" * 70)
        print("CAPTURA FINALIZADA")
        print("=" * 70)

        await browser.close()


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

async def main():

    try:

        await run_detector()

    except Exception as error:

        print("")
        print("=" * 70)
        print("ERRO GERAL DO SCANNER")
        print("=" * 70)

        print("")
        print(
            "ERRO:",
            str(error)
        )

        print("")
        print("TRACEBACK:")
        print("")

        traceback.print_exc()

        sys.exit(1)


# ==========================================================
# INICIAR
# ==========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
