#!/usr/bin/env python3
"""
sanitizar.py - harness de protecao de dado sensivel

Roda ANTES de mandar qualquer anotacao para um modelo de IA.

  1. le o arquivo de anotacao crua
  2. mascara credenciais, tokens, chaves, PII, IPs e dominios de cliente
  3. grava a versao sanitizada (esta sim pode ir para o modelo)
  4. grava um MAPA LOCAL de substituicao (nunca sai da maquina)
  5. mostra um relatorio do que foi mascarado

NAO envia nada para lugar nenhum e NAO altera o arquivo original.

USO
  python sanitizar.py anotacao.txt
  python sanitizar.py anotacao.txt --revisar
  python sanitizar.py anotacao.txt --manter-ip 10.0.0. --manter-dominio lab.local
  python sanitizar.py anotacao.txt --saida limpo.txt --mapa mapa.json
"""

import argparse
import difflib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ordem importa: o mais especifico primeiro, para nao mascarar pedaco do outro
PADROES = [
    ("CHAVE_PRIVADA",
     r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),

    # grupo 1 = rotulo (mantido), grupo 2 = separador (mantido), grupo 3 = valor (mascarado)
    ("CREDENCIAL",
     r"(?i)\b(senha|password|passwd|pwd|pass|secret|api[_-]?key|token|apikey)"
     r"(\s*[:=]\s*)[\"']?([^\s\"',;]{3,})"),

    ("CREDENCIAL_ASPAS",
     r"(?i)\b[\"']?(senha|password|passwd|pwd|secret|token)[\"']?\s*[:=]\s*[\"'][^\"']{3,}[\"']"),

    ("TOKEN_OPENAI",    r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
    ("TOKEN_ANTHROPIC", r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b"),
    ("TOKEN_GITHUB",    r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"),
    ("TOKEN_GITLAB",    r"\bglpat-[A-Za-z0-9_\-]{18,}\b"),
    ("AWS_KEY",         r"\bAKIA[0-9A-Z]{16}\b"),
    ("AWS_SECRET",      r"(?i)aws_secret_access_key\s*[:=]\s*[A-Za-z0-9/+=]{30,}"),
    ("SLACK",           r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b"),
    ("JWT",             r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b"),
    ("BEARER",          r"(?i)\b(bearer)\s+[A-Za-z0-9\-._~+/]{12,}"),

    # grupo 1 = parte do server (mantida), grupo 2 = senha (mascarada)
    ("CONNSTRING",
     r"(?i)((?:server|host|data source|endpoint)\s*=\s*[^;\n]+;[^\n]*?)"
     r"((?:password|pwd)\s*=\s*[^;\n]+)"),

    ("HASH_SHA256",     r"\b[a-fA-F0-9]{64}\b"),
    ("HASH_MD5",        r"\b[a-fA-F0-9]{32}\b"),
    ("CPF",            r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    ("CNPJ",           r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"),
    ("EMAIL",          r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"),
    ("TELEFONE",       r"(?:\+55\s*)?\(?\b\d{2}\)?\s*9?\d{4}[-\s]?\d{4}\b"),
    ("IP",             r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),

    # TLDs LONGOS PRIMEIRO: a alternancia para no primeiro match,
    # entao "com.br" precisa vir antes de "com".
    ("DOMINIO",        r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
                       r"(?:localdomain|internal|local|com\.br|corp|lan|net|org|io|com)\b"),
]

PRIVADOS = re.compile(r"^(10\.|127\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)")


def sanitizar(texto, manter_ip=(), manter_dominio=()):
    """Retorna (texto_sanitizado, mapa, estatisticas)."""
    mapa, stats = {}, {}
    contador = 0

    def marcador(tipo, original):
        nonlocal contador
        contador += 1
        token = f"<<{tipo}_{contador}>>"
        mapa[token] = original
        stats[tipo] = stats.get(tipo, 0) + 1
        return token

    out = texto

    # whitelist primeiro: protege os valores que devem aparecer
    protegidos = {}
    for i, ip in enumerate(sorted(set(manter_ip), key=len, reverse=True)):
        k, protegidos[k] = f"\x00IPW{i}\x00", ip
        out = out.replace(ip, k)
    for i, dom in enumerate(sorted(set(manter_dominio), key=len, reverse=True)):
        k, protegidos[k] = f"\x00DOMW{i}\x00", dom
        out = out.replace(dom, k)

    for tipo, pat in PADROES:
        def repl(m, _tipo=tipo):
            bruto = m.group(0)
            if _tipo == "IP":
                return marcador("IP_PRIVADO" if PRIVADOS.match(bruto) else "IP_PUBLICO", bruto)
            if _tipo == "CREDENCIAL":
                # mantem rotulo e separador, mascara apenas o valor
                return m.group(1) + m.group(2) + marcador("CREDENCIAL", m.group(3))
            if _tipo == "CONNSTRING":
                # mascara so a senha, preservando server/database
                return m.group(1) + marcador("CONNSTRING", m.group(2))
            return marcador(_tipo, bruto)
        out = re.sub(pat, repl, out)

    for k, v in protegidos.items():
        out = out.replace(k, v)

    return out, mapa, stats


def main():
    ap = argparse.ArgumentParser(description="Mascara dado sensivel antes de enviar para IA.")
    ap.add_argument("arquivo")
    ap.add_argument("--saida")
    ap.add_argument("--mapa")
    ap.add_argument("--manter-ip", nargs="*", default=[])
    ap.add_argument("--manter-dominio", nargs="*", default=[])
    ap.add_argument("--revisar", action="store_true")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()

    src = Path(a.arquivo)
    if not src.exists():
        print(f"ERRO: nao achei {src}", file=sys.stderr)
        return 2

    texto = src.read_text(encoding="utf-8", errors="replace")
    limpo, mapa, stats = sanitizar(texto, a.manter_ip, a.manter_dominio)

    base = src.with_suffix("")
    saida = Path(a.saida) if a.saida else Path(f"{base}.sanitizado.txt")
    mapa_p = Path(a.mapa) if a.mapa else Path(f"{base}.mapa-local.json")

    print("=" * 62)
    print(f"HARNESS DE SANITIZACAO - {src.name}")
    print("=" * 62)
    print(f"bytes de entrada : {len(texto):,}")
    print(f"bytes de saida   : {len(limpo):,}")
    if a.manter_ip:
        print(f"IPs preservados  : {', '.join(a.manter_ip)}")
    if a.manter_dominio:
        print(f"dominios preserv.: {', '.join(a.manter_dominio)}")
    print()

    if not stats:
        print("NENHUM padrao sensivel encontrado.")
        if not a.forcar:
            print("\nNada foi gravado. Use --forcar para gravar mesmo assim.")
            print("ATENCAO: ausencia de match NAO garante ausencia de segredo.")
            return 0

    total = sum(stats.values())
    print(f"MARCADORES APLICADOS: {total}")
    for tipo, n in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"   {n:>3}x  {tipo}")
    print()

    if a.revisar:
        print("--- REVISAO (so o que mudou) ---")
        dif = difflib.unified_diff(
            texto.splitlines(), limpo.splitlines(),
            fromfile="original", tofile="sanitizado", lineterm="", n=0)
        for linha in dif:
            if linha.startswith(("---", "+++", "@@")):
                continue
            if linha.startswith("-"):
                print(f"  ANTES : {linha[1:]}")
            elif linha.startswith("+"):
                print(f"  DEPOIS: {linha[1:]}")
        print()

    saida.write_text(limpo, encoding="utf-8")
    mapa_p.write_text(json.dumps({
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "arquivo_origem": str(src),
        "estatisticas": stats,
        "mapa": mapa,
        "aviso": "ARQUIVO LOCAL. NUNCA ENVIE PARA MODELO, CHAT OU REPOSITORIO PUBLICO.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"sanitizado  -> {saida}")
    print(f"mapa local  -> {mapa_p}   (NUNCA sai da maquina)")
    print()
    print("PROXIMO PASSO: mande o arquivo sanitizado para o modelo, nao o original.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
