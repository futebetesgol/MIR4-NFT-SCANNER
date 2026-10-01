import asyncio
import json
import os
from datetime import datetime, timezone

from xdraco_scanner import inspect_nft


# ==========================================================
# MIR4 NFT SCANNER
# ==========================================================
# REGRAS PRINCIPAIS:
#
# CLASSE: ARBALISTA
# POWER: 500.000 OU MENOS
# FOCO: EVA >= 5.000
# PRIORIDADE:
#   1 - EVA
#   2 - CRIT EVA
#   3 - Skill DMG Reduction
#   4 - PvP DMG Reduction
#   5 - All DMG Reduction
#
# IMPORTANTE:
# Este arquivo executa a coleta.
# A análise completa dos decks será adicionada
# depois de validarmos a coleta real do XDRACO.
# ==========================================================


MAX_POWER = 500_000
MIN_EVA = 5_000


# ==========================================================
# IDs PARA TESTE
# ==========================================================
# Primeiro vamos testar poucos NFTs.
# Depois substituiremos isto pela descoberta automática
# dos NFTs disponíveis no marketplace.
# ==========================================================

TEST_TRADE_IDS = [
    "2330341",
]


# ==========================================================
# ANALISAR UM NFT
# ==========================================================

async def scan_one(trade_id):

    print("=" * 60)
    print(f"Analisando NFT: {trade_id}")

    try:

        result = await inspect_nft(trade_id)

        if not result:
            print("Nenhum resultado.")
            return None

        if not result.get(
            "approved_basic_filter",
            False
        ):
            print(
                "NFT eliminado pelo filtro inicial."
            )

            return None

        power = result.get(
            "power",
            0
        )

        if power > MAX_POWER:

            print(
                f"ELIMINADO: Power {power} "
                f"acima de {MAX_POWER}"
            )

            return None

        print(
            f"APROVADO NO FILTRO INICIAL: "
            f"{power} Power"
        )

        return result

    except Exception as error:

        print(
            f"ERRO NO NFT {trade_id}: "
            f"{error}"
        )

        return None


# ==========================================================
# EXECUTAR SCANNER
# ==========================================================

async def main():

    print("")
    print("==========================================")
    print("       MIR4 NFT SCANNER INICIADO")
    print("==========================================")
    print("")

    print(
        "Classe procurada: ARBALISTA"
    )

    print(
        "Power máximo: 500.000"
    )

    print(
        "EVA desejada: 5.000+"
    )

    print("")

    results = []

    for trade_id in TEST_TRADE_IDS:

        result = await scan_one(
            trade_id
        )

        if result:
            results.append(result)

        # Pequeno intervalo entre requisições
        await asyncio.sleep(2)

    # ======================================================
    # CRIAR PASTA DO SITE
    # ======================================================

    os.makedirs(
        "docs",
        exist_ok=True
    )

    # ======================================================
    # ARQUIVO FINAL
    # ======================================================

    output = {

        "scanner":
            "MIR4 NFT Scanner",

        "updated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "rules": {

            "class":
                "Arbalista",

            "max_power":
                MAX_POWER,

            "minimum_target_eva":
                MIN_EVA,

            "priority": [
                "EVA",
                "CRIT EVA",
                "Skill DMG Reduction",
                "PvP DMG Reduction",
                "All DMG Reduction"
            ]
        },

        "total_found":
            len(results),

        "results":
            results
    }

    # ======================================================
    # SALVAR JSON
    # ======================================================

    with open(
        "docs/results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("")
    print("==========================================")
    print(
        f"SCANNER FINALIZADO - "
        f"{len(results)} resultado(s)"
    )
    print("==========================================")
    print("")

    print(
        "Arquivo criado: docs/results.json"
    )


# ==========================================================
# INICIAR
# ==========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
