#!/usr/bin/env python3
"""
wizard.py — configure seu segundo cerebro em 5 minutos
======================================================
Um guia interativo que gera o material no formato que a IA consegue processar.

O problema que ele resolve: IA nao organiza material ambiguo. Se o arquivo nao
disser O QUE deve ser entregue, QUAL o limite, QUAIS os passos e COMO saber que
acabou, o agente para (e esta certo em parar).

O wizard pergunta essas quatro coisas e monta o arquivo pronto.

USO
  python wizard/wizard.py                    # interativo
  python wizard/wizard.py --area red-team    # parte de um exemplo da sua area
  python wizard/wizard.py --check meu.txt    # valida um arquivo existente
  python wizard/wizard.py --areas            # lista as areas com exemplo

Depois de gerar o arquivo:
  1. python harness/sanitizar.py <arquivo>          # protege dado sensivel
  2. mande o arquivo .sanitizado.txt para a IA
"""

import argparse
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------- areas
AREAS = {
    "red-team": {
        "nome": "Red team / pentest",
        "objetivo": "Documentar a tecnica executada para que seja reproduzivel e defensavel",
        "fora": "persistencia sem autorizacao, dump de credencial, exfiltracao de dado real",
        "etapas": [
            ("Acesso inicial", "como entrei, qual servico, qual falha permitiu"),
            ("Escalacao", "quais privilegios eu tinha e qual deles permitiu subir"),
            ("Impacto", "o que fiquei capaz de fazer e o que NAO fiz por escopo"),
        ],
        "criterio": "nota com comando exato, saida obtida, o privilegio que permitiu, "
                    "mapeamento ATT&CK com sub-tecnica, deteccao e mitigacao",
    },
    "desenvolvimento": {
        "nome": "Desenvolvimento de software",
        "objetivo": "Registrar a decisao tecnica para que ninguem a desfaca sem entender o motivo",
        "fora": "modulos nao afetados, migracao de dado historico",
        "etapas": [
            ("Avaliacao", "quais alternativas considerei e por que descartei cada uma"),
            ("Implementacao", "o que mudou de fato, arquivo por arquivo"),
            ("Validacao", "como provei que funciona (teste, benchmark, metrica)"),
        ],
        "criterio": "registro com alternativas descartadas e o motivo, numeros de antes e depois, "
                    "como reverter, e o que ainda nao tem cobertura de teste",
    },
    "infraestrutura": {
        "nome": "Infraestrutura / operacao",
        "objetivo": "Registrar a mudanca com rollback completo, para reverter as 3h da manha",
        "fora": "ambientes nao envolvidos, sistemas de terceiro",
        "etapas": [
            ("Diagnostico", "qual era o estado antes e qual o sintoma"),
            ("Execucao", "o que foi alterado, com o valor anterior registrado"),
            ("Validacao", "como confirmei que voltou a funcionar"),
        ],
        "criterio": "nota com configuracao anterior e nova (diff), comandos de rollback testados, "
                    "hosts validados e o que nao foi testado em producao",
    },
    "juridico": {
        "nome": "Juridico / analise",
        "objetivo": "Registrar fatos, provas e tese para escrever a peca sem depender da memoria",
        "fora": "pedidos sem prova, questoes de outra area",
        "etapas": [
            ("Fatos", "o que aconteceu, com data quando houver"),
            ("Provas", "o que sustenta cada fato e o que esta faltando"),
            ("Tese", "o fundamento e os pedidos, cada um com sua prova"),
        ],
        "criterio": "cada fato ligado a uma prova, cada pedido com fundamento e precedente, "
                    "e a lista explicita do que NAO foi alegado por falta de prova",
    },
    "dados": {
        "nome": "Analise de dados / pesquisa",
        "objetivo": "Registrar a analise para que o resultado seja reproduzivel por outra pessoa",
        "fora": "fontes nao validadas, recortes nao justificados",
        "etapas": [
            ("Pergunta", "qual pergunta eu queria responder e por que ela importa"),
            ("Metodo", "qual fonte, qual filtro, qual transformacao"),
            ("Resultado", "o que encontrei e qual a margem de erro ou limitacao"),
        ],
        "criterio": "pergunta, fonte, filtro e transformacao registrados o suficiente para "
                    "outra pessoa refazer e chegar ao mesmo numero",
    },
}

# ---------------------------------------------------------------- utils
def perguntar(rotulo, padrao="", obrigatorio=True, dica=""):
    """Pergunta com default e validacao."""
    marca = f" [{padrao}]" if padrao else ""
    while True:
        if dica:
            print(f"    ({dica})")
        try:
            resp = input(f"  {rotulo}{marca}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\ncancelado.")
            sys.exit(0)
        if not resp and padrao:
            return padrao
        if resp or not obrigatorio:
            return resp
        print("    ^ precisa de uma resposta (Enter vazio nao vale)\n")

def cabecalho(txt):
    print()
    print("=" * 64)
    print(f"  {txt}")
    print("=" * 64)

def gerar(area, projeto, objetivo, dentro, fora, etapas, criterio, observacoes):
    hoje = datetime.now().strftime("%Y-%m-%d")
    linhas = [
        f"# {projeto}",
        f"# gerado pelo wizard em {hoje}",
        f"# area: {area}",
        "",
        "## OBJETIVO",
        objetivo,
        "",
        "## ESCOPO",
        "DENTRO:",
        *[f"  - {d}" for d in dentro],
        "",
        "FORA:",
        *[f"  - {f}" for f in fora],
        "",
        "## ETAPAS",
        "",
    ]
    for i, (nome, desc) in enumerate(etapas, 1):
        linhas += [f"### {i} - {nome}", desc, ""]
    linhas += ["## CRITERIO DE ACEITACAO", criterio, ""]
    if observacoes:
        linhas += ["## OBSERVACOES", observacoes, ""]
    linhas += [
        "## O QUE EU NAO TESTEI",
        "  [ ] (preencher — esta e a lista que evita susto no relatorio)",
        "",
        "## REGRAS",
        "  1. Registrar no momento, nao depois",
        "  2. Separar fato de hipotese: confirmado / inferido / nao testado",
        "  3. Registrar o que NAO foi testado",
        "  4. Ligar esta nota as notas relacionadas",
    ]
    return "\n".join(linhas) + "\n"

# ---------------------------------------------------------------- check
CAMPOS = {
    "OBJETIVO": r"##\s*OBJETIVO",
    "ESCOPO": r"##\s*ESCOPO",
    "ETAPAS": r"###\s*\d+",
    "CRITERIO DE ACEITACAO": r"##\s*CRITERI[OA]\s+DE\s+ACEITA",
}

def validar(caminho):
    import re
    p = Path(caminho)
    if not p.exists():
        print(f"ERRO: nao achei {p}")
        return 2
    txt = p.read_text(encoding="utf-8", errors="replace")
    print(f"\nVALIDANDO: {p.name}  ({len(txt):,} bytes)\n")
    faltando = []
    for nome, pat in CAMPOS.items():
        if re.search(pat, txt, re.I):
            print(f"  OK      {nome}")
        else:
            print(f"  FALTA   {nome}")
            faltando.append(nome)
    # conta etapas
    n_etapas = len(re.findall(r"###\s*\d+", txt))
    if n_etapas:
        print(f"\n  etapas numeradas: {n_etapas}")
    print()
    if faltando:
        print("RESULTADO: o agente provavelmente vai PARAR e pedir esses campos.")
        print("Campo que falta:", ", ".join(faltando))
        print("\nPor que ele para: sem escopo e sem criterio, ele nao consegue")
        print("distribuir o trabalho nem saber quando terminou.")
        return 1
    print("RESULTADO: material valido. Proximo passo:")
    print(f"  python harness/sanitizar.py {p.name}")
    return 0

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Wizard de configuracao do segundo cerebro.")
    ap.add_argument("--area", choices=list(AREAS), help="parte de um exemplo da sua area")
    ap.add_argument("--check", metavar="ARQUIVO", help="valida um arquivo existente")
    ap.add_argument("--areas", action="store_true", help="lista as areas disponiveis")
    ap.add_argument("--saida", help="nome do arquivo (default: <projeto>.txt)")
    ap.add_argument("--nao-interativo", action="store_true",
                    help="usa o padrao da area sem perguntar (para testar)")
    a = ap.parse_args()

    if a.areas:
        print("\nAreas com exemplo pronto:\n")
        for k, v in AREAS.items():
            print(f"  {k:<16} {v['nome']}")
        print("\nUse:  python wizard/wizard.py --area <area>\n")
        return 0

    if a.check:
        return validar(a.check)

    if a.nao_interativo and a.area:
        area_dados = AREAS[a.area]
        etapas = area_dados["etapas"]
        out = gerar(
            area=a.area,
            projeto=f"exemplo-{a.area}",
            objetivo=area_dados["objetivo"],
            dentro=["(preencher: o que esta incluido)", "(preencher: ativos, modulos ou partes)"],
            fora=[area_dados["fora"]],
            etapas=etapas,
            criterio=area_dados["criterio"],
            observacoes="",
        )
        nome = a.saida or f"exemplo-{a.area}.txt"
        Path(nome).write_text(out, encoding="utf-8")
        print(f"gerado: {nome} ({len(out):,} bytes)")
        return 0

    cabecalho("WIZARD — segundo cerebro em 5 minutos")
    print("""
  Vou fazer 5 perguntas. O resultado e um arquivo que a IA consegue
  processar sem travar e sem inventar.

  Regra: se voce nao consegue responder o criterio de aceitacao,
  o material ainda nao esta pronto — e o wizard vai te dizer isso.
""")

    print("  AREAS DISPONIVEIS:")
    for i, (k, v) in enumerate(AREAS.items(), 1):
        print(f"    {i}. {v['nome']}  ({k})")
    print(f"    {len(AREAS)+1}. Outra / prefiro descrever")

    escolha = perguntar("numero da area", "1")
    chaves = list(AREAS)
    if escolha.isdigit() and 1 <= int(escolha) <= len(chaves):
        area_key = chaves[int(escolha) - 1]
        base = AREAS[area_key]
        print(f"\n  -> usando base: {base['nome']} (voce pode ajustar tudo)\n")
    else:
        area_key = "personalizado"
        base = {"nome": "personalizado", "objetivo": "", "fora": "", "etapas": [], "criterio": ""}

    projeto = perguntar("nome do projeto ou do trabalho", "meu-projeto")
    cabecalho("1/5  OBJETIVO")
    print("  O que esta documentacao precisa entregar, em uma frase.\n")
    objetivo = perguntar("objetivo", base["objetivo"],
                         dica="ex: registrar a mudanca de rede com rollback completo")

    cabecalho("2/5  ESCOPO — o que esta DENTRO")
    print("  Um item por linha. Enter vazio para terminar.\n")
    dentro = []
    while True:
        item = perguntar(f"dentro [{len(dentro)+1}]", obrigatorio=False)
        if not item:
            if dentro:
                break
            print("    ^ pelo menos um item\n")
            continue
        dentro.append(item)

    cabecalho("3/5  ESCOPO — o que esta FORA")
    print("  O limite explicito. E isso que impede o agente de inventar.\n")
    fora = []
    padrao_fora = [base["fora"]] if base.get("fora") else []
    for p in padrao_fora:
        resp = perguntar("fora (Enter aceita o padrao)", p, obrigatorio=False)
        if resp:
            fora.append(resp)
    while True:
        item = perguntar(f"fora [{len(fora)+1}]", obrigatorio=False)
        if not item:
            break
        fora.append(item)

    cabecalho("4/5  ETAPAS")
    print("  Os passos, em ordem. Sao eles que viram os cards do Kanban.\n")
    etapas = []
    if base.get("etapas"):
        print("  Sugestao da sua area:")
        for i, (n, d) in enumerate(base["etapas"], 1):
            print(f"    {i}. {n}")
        usar = perguntar("usar essas etapas? (s/n)", "s")
        if usar.lower().startswith("s"):
            etapas = list(base["etapas"])
    while True:
        nome = perguntar(f"etapa [{len(etapas)+1}] nome (Enter vazio encerra)", obrigatorio=False)
        if not nome:
            if etapas:
                break
            print("    ^ pelo menos uma etapa\n")
            continue
        desc = perguntar(f"etapa [{len(etapas)+1}] o que acontece", obrigatorio=False)
        etapas.append((nome, desc))

    cabecalho("5/5  CRITERIO DE ACEITACAO")
    print("  Como saber que a nota ficou completa.")
    print("  Sem isso, nada termina — e o agente vai recusar.\n")
    criterio = perguntar("criterio", base["criterio"],
                         dica="ex: nota com comando, saida, e o que NAO foi testado")

    cabecalho("OBSERVACOES (opcional)")
    obs = perguntar("algo mais que deva entrar", obrigatorio=False)

    out = gerar(area_key, projeto, objetivo, dentro, fora, etapas, criterio, obs)
    nome = a.saida or f"{projeto}.txt"
    Path(nome).write_text(out, encoding="utf-8")

    cabecalho("PRONTO")
    print(f"  arquivo gerado: {nome}  ({len(out):,} bytes)\n")
    print("  VALIDANDO os 4 campos obrigatorios:")
    ok = True
    for campo in CAMPOS:
        presente = campo.lower().split()[0] in out.lower()
        print(f"    {'OK   ' if presente else 'FALTA'} {campo}")
        ok = ok and presente
    print()
    print("  PROXIMOS PASSOS:")
    print(f"    1. python harness/sanitizar.py {nome} --revisar")
    print(f"    2. mandar o arquivo .sanitizado.txt para a IA")
    print(f"    3. conferir de novo:  python wizard/wizard.py --check {nome}")
    if not ok:
        print("\n  AVISO: algum campo ficou vazio. O agente vai parar e pedir.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
