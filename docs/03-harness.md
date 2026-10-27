# O harness de sanitização

## O problema que ninguém pensa

Ao mandar anotação crua para uma API de LLM, ela **sai da sua máquina**.
Se tiver senha, token, CPF ou nome de cliente, você vazou — e não tem desfazer.

Documentar com IA não pode ser um atalho para quebrar sigilo profissional.

## A arquitetura

```
anotação crua
      │
      ▼
┌─────────────────┐
│    HARNESS      │  roda LOCAL, antes de qualquer envio
│  sanitizar.py   │
└────────┬────────┘
         │
    ┌────┴─────┐
    ▼          ▼
versão      mapa local
sanitizada  (fica na máquina, nunca sai)
    │
    ▼
 MODELO  ← só vê marcadores: <<CREDENCIAL_2>>, <<IP_PRIVADO_13>>
    │
    ▼
  notas no acervo
    │
    ▼
você devolve os valores reais manualmente, se precisar
```

**O princípio:** o modelo recebe `<<CREDENCIAL_2>>`, não `Pr0d@2024!xyz`.
Ele organiza a nota ("havia uma credencial no arquivo de configuração") **sem nunca
ter acesso à credencial**.

## Uso

```bash
# sanitizar
python harness/sanitizar.py anotacoes.txt

# revisar o que foi mascarado (na primeira vez, sempre)
python harness/sanitizar.py anotacoes.txt --revisar

# cenário fictício? preserve os valores sintéticos
python harness/sanitizar.py anotacoes.txt --manter-ip 10.0.0. --manter-dominio lab.local

# mande o .sanitizado.txt, nunca o original
```

Saída real:

```
==============================================================
HARNESS DE SANITIZACAO — teste-sensivel.txt
==============================================================
bytes de entrada : 972
bytes de saida   : 751

MARCADORES APLICADOS: 19
     4x  IP_PRIVADO
     3x  CREDENCIAL
     3x  DOMINIO
     1x  CHAVE_PRIVADA
     1x  TOKEN_OPENAI
     1x  TOKEN_GITHUB
     1x  AWS_KEY
     1x  CPF
     1x  CNPJ
     1x  EMAIL
     1x  TELEFONE
```

## O que mascara

| Categoria | Padrões |
|---|---|
| Credencial nomeada | `senha:` `password=` `pwd` `api_key:` `token:` `secret:` |
| Tokens | `sk-…` `ghp_…` `gho_…` `glpat-…` `AKIA…` `xox[baprs]-…` JWT Bearer |
| Chave privada | bloco `BEGIN … PRIVATE KEY` inteiro |
| Connection string | só a parte `Password=` (preserva server e database) |
| PII | e-mail, telefone, CPF, CNPJ |
| Infraestrutura | IP privado, IP público, domínio de cliente |
| Hash | SHA-256, MD5 (configurável) |

## Três decisões de design

**1. O rótulo fica, o valor sai.**
`senha: <<CREDENCIAL_2>>` — não `<<CREDENCIAL_2>>` sozinho. O modelo precisa
saber *que era uma senha*.

**2. TLDs longos primeiro no regex.**
`com.br` antes de `com`, senão `dominio.com.br` vira `<<DOMINIO>>.br`.
Não vaza, mas quebra a legibilidade do material.

**3. Hash pode passar.**
SHA-256 não reverte para o conteúdo e muitas vezes é útil ao modelo
(comparar com base de IOC). Se o hash for de arquivo sensível, mantenha o padrão.

## Limites honestos

- **Não adivinha.** Padrão fora da lista passa adiante. Por isso o `--revisar`.
- **Ausência de match não é prova de segurança.** "Nenhum padrão encontrado"
  significa "nada que eu conheça". A responsabilidade final é humana.
- **Não envia nada.** Só escreve dois arquivos locais.

> ⚠️ O `*.mapa-local.json` contém **os valores reais**. É o arquivo mais sensível
> de todo o processo. Nunca em repositório, chat, nuvem pública ou prompt.
> O próprio arquivo carrega esse aviso dentro dele.
