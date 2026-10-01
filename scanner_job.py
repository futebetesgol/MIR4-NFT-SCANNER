# ==========================================================
# MIR4 NFT SCANNER
# EXECUTOR DO DETECTOR XDRACO
# ==========================================================
#
# Este arquivo é executado pelo GitHub Actions.
#
# OBJETIVO ATUAL:
# - Abrir um NFT real do XDRACO
# - Usar Chromium/Playwright
# - Detectar as requisições internas do site
# - Descobrir de onde vêm os dados do personagem
#
# Depois vamos usar esses dados para:
#
# - Somente ARBALISTA
# - Power máximo: 500.000
# - EVA mínima desejada: 5.000+
# - Prioridade máxima para EVA
# - Prioridade alta para CRIT EVA
# - Skill DMG Reduction
# - PvP DMG Reduction
# - All DMG Reduction
# - Decks 1 até 10
# - Spirits/Pets
# - Tesouros dos Pets
# - Magic Stones
# - Atributos das pedras
# - Mystical Pieces
# - Atributos das peças
# - Constitution
# - Potential
# - Conquest/Torres
# - Skills
# - Equipamentos
# - Link direto do NFT
#
# ==========================================================


import asyncio
import sys
import traceback


# ==========================================================
# IMPORTAR DETECTOR
# ==========================================================

try:

    from xdraco_detector import main as detector_main

except Exception as error:

    print("")
    print("=" * 70)
    print("ERRO AO IMPORTAR XDRACO DETECTOR")
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
# EXECUTAR
# ==========================================================

async def run():

    print("")
    print("=" * 70)
    print("            MIR4 NFT SCANNER")
    print("=" * 70)
    print("")

    print("CONFIGURAÇÃO DA BUSCA:")
    print("")

    print(
        "Classe...............: ARBALISTA"
    )

    print(
        "Power máximo.........: 500.000"
    )

    print(
        "EVA desejada.........: 5.000+"
    )

    print(
        "Prioridade #1........: EVA"
    )

    print(
        "Prioridade #2........: CRIT EVA"
    )

    print(
        "Prioridade #3........: Skill DMG Reduction"
    )

    print(
        "Prioridade #4........: PvP DMG Reduction"
    )

    print(
        "Prioridade #5........: All DMG Reduction"
    )

    print("")
    print(
        "Modo atual...........: DETECTOR XDRACO"
    )

    print("")
    print("=" * 70)
    print("INICIANDO DETECTOR...")
    print("=" * 70)
    print("")

    try:

        await detector_main()

    except Exception as error:

        print("")
        print("=" * 70)
        print("ERRO DURANTE A EXECUÇÃO")
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

    print("")
    print("=" * 70)
    print("DETECTOR FINALIZADO")
    print("=" * 70)
    print("")


# ==========================================================
# INÍCIO
# ==========================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            run()
        )

    except KeyboardInterrupt:

        print("")
        print(
            "Scanner interrompido."
        )

        sys.exit(0)
