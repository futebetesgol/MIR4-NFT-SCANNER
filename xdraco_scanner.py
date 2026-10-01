import asyncio
import json
from playwright.async_api import async_playwright


TRADE_ID = "2330341"
XDRACO_URL = f"https://www.xdraco.com/nft/trade/{TRADE_ID}"


async def main():

    print("")
    print("=" * 70)
    print("       MIR4 - DETECTOR DE DADOS DO XDRACO")
    print("=" * 70)
    print("")
    print("NFT:", TRADE_ID)
    print("URL:", XDRACO_URL)
    print("")

    captured = []
    character_summary = None

    async with async_playwright() as p:

        browser = await p.chromium.launch(
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

        async def handle_response(response):

            nonlocal character_summary

            try:

                request = response.request
                resource_type = request.resource_type

                content_type = (
                    response.headers.get(
                        "content-type",
                        ""
                    )
                ).lower()

                url = response.url

                interesting = (
                    resource_type in [
                        "xhr",
                        "fetch",
                    ]
                    or "json" in content_type
                )

                if not interesting:
                    return

                print("")
                print("------------------------------------------")
                print("RESPOSTA ENCONTRADA")
                print("------------------------------------------")
                print("STATUS:", response.status)
                print("TIPO:", resource_type)
                print("CONTENT-TYPE:", content_type)
                print("URL:", url)

                try:
                    body = await response.text()
                except Exception:
                    body = ""

                print("TAMANHO:", len(body))

                parsed_body = None

                if body:
                    try:
                        parsed_body = json.loads(body)
                    except Exception:
                        parsed_body = None

                item = {
                    "status": response.status,
                    "type": resource_type,
                    "content_type": content_type,
                    "url": url,
                }

                # Salvar resposta JSON quando existir
                if parsed_body is not None:
                    item["response"] = parsed_body

                captured.append(item)

                # ==================================================
                # CAPTURAR CHARACTER SUMMARY
                # ==================================================

                if "/nft/character/summary" in url:

                    print("")
                    print("=" * 70)
                    print(">>> CHARACTER SUMMARY ENCONTRADO <<<")
                    print("=" * 70)
                    print("")

                    if parsed_body is not None:

                        character_summary = {
                            "url": url,
                            "status": response.status,
                            "data": parsed_body,
                        }

                        print(
                            json.dumps(
                                parsed_body,
                                ensure_ascii=False,
                                indent=2
                            )[:15000]
                        )

                    else:

                        character_summary = {
                            "url": url,
                            "status": response.status,
                            "raw": body,
                        }

                        print(body[:15000])

                    print("")
                    print("=" * 70)

                # ==================================================
                # DIAGNÓSTICO
                # ==================================================

                if body:

                    lower = body.lower()

                    keywords = [
                        "power",
                        "powerscore",
                        "character",
                        "arbalist",
                        "spirit",
                        "stone",
                        "mystical",
                        "deck",
                        "evasion",
                        "crit",
                        "nft",
                        "class",
                        "level",
                    ]

                    found_keywords = []

                    for keyword in keywords:

                        if keyword in lower:
                            found_keywords.append(keyword)

                    if found_keywords:

                        print("")
                        print(">>> POSSÍVEL API IMPORTANTE <<<")

                        print(
                            "PALAVRAS:",
                            ", ".join(found_keywords)
                        )

                        preview = (
                            body[:3000]
                            .replace("\n", " ")
                            .replace("\r", " ")
                        )

                        print("")
                        print("INÍCIO DA RESPOSTA:")
                        print(preview)
                        print("")

            except Exception as error:

                print(
                    "Erro ao analisar resposta:",
                    str(error)
                )

        page.on(
            "response",
            handle_response
        )

        # ==================================================
        # ABRIR XDRACO
        # ==================================================

        print("Abrindo XDRACO...")
        print("")

        try:

            await page.goto(
                XDRACO_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

        except Exception as error:

            print(
                "Aviso ao carregar página:",
                str(error)
            )

        print(
            "Esperando o XDRACO carregar os dados..."
        )

        await page.wait_for_timeout(15000)

        # ==================================================
        # INFORMAÇÕES DA PÁGINA
        # ==================================================

        print("")
        print("=" * 70)
        print("INFORMAÇÕES DA PÁGINA")
        print("=" * 70)

        print(
            "URL FINAL:",
            page.url
        )

        print(
            "TÍTULO:",
            await page.title()
        )

        body_text = ""

        try:

            body_text = await page.locator(
                "body"
            ).inner_text(
                timeout=10000
            )

        except Exception:
            pass

        print(
            "TAMANHO DO TEXTO:",
            len(body_text)
        )

        print("")
        print("PALAVRAS NA PÁGINA RENDERIZADA:")

        for keyword in [
            "Power",
            "Arbalist",
            "Spirit",
            "Magic Stone",
            "Mystical Piece",
            "Evasion",
            "NFT",
        ]:

            exists = (
                keyword.lower()
                in body_text.lower()
            )

            print(
                keyword,
                "=",
                "SIM" if exists else "NÃO"
            )

        # ==================================================
        # TEXTO DA PÁGINA
        # ==================================================

        if body_text:

            print("")
            print("=" * 70)
            print("TEXTO RENDERIZADO - AMOSTRA")
            print("=" * 70)

            print(
                body_text[:5000]
            )

        # ==================================================
        # REMOVER URLs DUPLICADAS
        # ==================================================

        print("")
        print("=" * 70)
        print("REQUISIÇÕES XHR/FETCH ENCONTRADAS")
        print("=" * 70)

        unique = {}

        for item in captured:
            unique[item["url"]] = item

        for index, item in enumerate(
            unique.values(),
            start=1
        ):

            print("")
            print(f"[{index}]")

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

        # ==================================================
        # SALVAR TODAS AS REQUISIÇÕES
        # ==================================================

        with open(
            "xdraco_requests.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                list(unique.values()),
                file,
                ensure_ascii=False,
                indent=2,
            )

        print("")
        print(
            "Arquivo criado: xdraco_requests.json"
        )

        # ==================================================
        # SALVAR CHARACTER SUMMARY SEPARADAMENTE
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
            print("CHARACTER SUMMARY SALVO COM SUCESSO")
            print("=" * 70)
            print("")
            print(
                "Arquivo criado: character_summary.json"
            )

        else:

            print("")
            print("=" * 70)
            print("ATENÇÃO")
            print("=" * 70)
            print(
                "A API character/summary não foi capturada."
            )

        print("")
        print("=" * 70)
        print(
            f"TOTAL DE REQUISIÇÕES INTERESSANTES: "
            f"{len(unique)}"
        )
        print("=" * 70)

        await browser.close()


if __name__ == "__main__":

    asyncio.run(
        main()
    )
