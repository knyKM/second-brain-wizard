# Segundo Cérebro — Wizard de Configuração

> **Você resolve problemas difíceis e esquece como resolveu.**
> Este repositório configura um sistema para que isso pare de acontecer —
> com IA organizando o que você anota, e um harness que impede dado sensível de vazar.

Não é específico de segurança. Serve para **desenvolvimento, infraestrutura, jurídico,
análise de dados, pesquisa, operação** — qualquer atividade em que você produz
conhecimento e depois recomeça do zero.

---

## O problema

Você resolve algo difícil. Anota no bloco de notas, no chat, num print.
Três meses depois o mesmo problema aparece **e você recomeça**.

Não é falta de disciplina. É que **registrar dá trabalho na hora e o benefício
só aparece depois**. Quem paga a conta é o você do futuro.

E o agravante: o red team (ou o dev, ou o jurídico) gera muito conhecimento e retém
pouco. O gargalo nunca foi **produzir** — sempre foi **reter**.

---

## Como funciona (3 verbos)

| Verbo | O que é | Quem faz |
|---|---|---|
| **Capturar** | anotar do jeito que sair, sem formato | você |
| **Estruturar** | virar nota com forma fixa | a IA |
| **Reutilizar** | perguntar em vez de recomeçar | você, na próxima |

O formato é o que permite achar depois. E formato não é trabalho seu — é da IA.

---

## Quickstart (3 comandos)

```bash
git clone https://github.com/<seu-usuario>/second-brain-wizard.git
cd second-brain-wizard

# 1. o wizard pergunta 5 coisas e gera seu material
python wizard/wizard.py

# 2. o harness protege dado sensível ANTES de mandar para a IA
python harness/sanitizar.py meu-projeto.txt --revisar

# 3. mande o arquivo .sanitizado.txt para a IA
```

Sem dependência externa. Só Python 3.9+.

---

## Por que existe um wizard (e não só um template)

Porque o erro que **todos** cometem é o mesmo: entregar material ambíguo para a IA
e esperar que ela "dê um jeito".

Ela não dá. Um agente sério **para** e diz o que falta — e isso é uma virtude, não um defeito:

> *"Sem escopo e sem critério de aceitação, o card raiz viraria 8 cards sem como verificar
> conclusão — e o perfil não improvisa em cima de escopo ambíguo."*
> — resposta real de um agente ao receber material sem os campos

O wizard existe para você **não passar por isso**. Ele pergunta as quatro coisas que a IA precisa:

```
## OBJETIVO              o que a documentação tem que entregar
## ESCOPO               DENTRO: ...  /  FORA: ...   (o limite é o que impede invenção)
## ETAPAS               numeradas — é o que vira card no Kanban
## CRITERIO DE ACEITACAO como saber que acabou
```

Se você não consegue escrever o **critério de aceitação**, o material ainda não está
pronto. Escrever o critério é o que força você a saber o que queria.

---

## O harness (a parte que quase todo mundo esquece)

Quando você manda anotação crua para uma API de LLM, ela **sai da sua máquina**.
Se tiver senha, token, CPF ou nome de cliente, você vazou — e não tem desfazer.

**O dado sensível não atravessa a fronteira da máquina:**

```
anotação crua
      │
      ▼
┌──────────────┐
│   HARNESS    │  roda local, antes de qualquer envio
│ sanitizar.py │
└──────┬───────┘
       │
   ┌───┴────┐
   ▼        ▼
sanitizada  mapa local
   │        (fica na máquina)
   ▼
 MODELO  ← só vê <<CREDENCIAL_2>>, nunca a senha
```

O modelo recebe `<<CREDENCIAL_2>>` e documenta *"havia uma credencial no arquivo de
configuração"* — que é toda a informação de que ele precisa.

```bash
python harness/sanitizar.py anotacoes.txt --revisar
```

| Mascara | Exemplo |
|---|---|
| Credencial nomeada | `senha:` `password=` `api_key:` `token:` |
| Tokens | `sk-…` `ghp_…` `glpat-…` `AKIA…` `xoxb-…` JWT |
| Chave privada | bloco `BEGIN…PRIVATE KEY` inteiro |
| Connection string | só `Password=`, preserva server/database |
| PII | e-mail, telefone, CPF, CNPJ |
| Infra | IP privado/público, domínio de cliente |

**Limites honestos:** ele não adivinha (por isso o `--revisar`), e ausência de match
não é prova de segurança. "Nenhum padrão encontrado" significa "nada que eu conheça".

> ⚠️ O `*.mapa-local.json` contém os valores reais. Nunca em repositório, chat ou nuvem.

---

## Áreas com exemplo pronto

```bash
python wizard/wizard.py --areas
```

| Área | O que o wizard configura |
|---|---|
| `red-team` | técnica documentada com ATT&CK, detecção e mitigação |
| `desenvolvimento` | decisão de arquitetura com alternativas descartadas |
| `infraestrutura` | mudança com rollback testado |
| `juridico` | fatos, provas e tese — sem alegar o que não tem prova |
| `dados` | análise reproduzível por outra pessoa |

Os 5 exemplos estão em [`exemplos/`](exemplos/).

---

## Validando antes de mandar

```bash
python wizard/wizard.py --check meu-projeto.txt
```

```
VALIDANDO: meu-projeto.txt  (1.038 bytes)

  OK      OBJETIVO
  OK      ESCOPO
  OK      ETAPAS
  OK      CRITERIO DE ACEITACAO

  etapas numeradas: 3

RESULTADO: material valido. Proximo passo:
  python harness/sanitizar.py meu-projeto.txt
```

Se faltar campo, ele diz **qual** e **por que** o agente vai parar.

---

## O que você faz com o material depois

O arquivo gerado é a **entrada**. A saída é a nota estruturada no seu acervo
(Obsidian, Notion, pasta com git — qualquer coisa pesquisável).

Prompt para colar no seu agente:

```text
@file:<arquivo>.sanitizado.txt

Estas são minhas anotações cruas sobre este trabalho.

Documenta no meu acervo, no projeto "<NOME>":

- o que foi feito, em ordem
- o que foi descoberto ou decidido, com a evidência que sustenta cada ponto
- o que ficou em aberto e o que falta para fechar
- as dúvidas registradas, sem inventar resposta
- as lições que servem para a próxima vez

Regras:
1. NÃO invente nada que não esteja nas anotações.
2. O que completar com conhecimento próprio marca como INFERIDO, nunca CONFIRMADO.
3. Se faltar informação, registra a lacuna em vez de preencher.
4. Cria o índice e liga as notas com wikilinks.
5. Credencial ou segredo: registra existência e local, mascara o valor, me avisa.
```

---

## Filosofia (o que faz isso funcionar)

1. **A recusa é uma feature.** Agente que aceita material ambíguo produz documento
   bonito e vazio. Agente que para e diz o que falta está trabalhando pra você.
2. **Separe fato de hipótese.** `CONFIRMADO` / `INFERIDO` / `NÃO TESTADO` — três estados, nunca dois.
3. **Registre o que você NÃO testou.** Vale mais que a lista do que testou.
4. **O valor mora na ligação.** Uma nota isolada é um arquivo. Duas notas ligadas são conhecimento.
5. **Comece pequeno.** Uma coisa que você repete toda semana. Passo a passo, uma vez.

---

## O teste que quase ninguém faz

> Abra sua própria nota de seis meses atrás.
> **Você consegue executar o que está escrito, sem pensar?**
>
> Se a resposta for "quase", você acabou de encontrar o seu problema.

Documentação não falha quando você escreve. Falha quando **outra pessoa** — ou você
no futuro — tenta usar.

---

## Estrutura do repositório

```
wizard/wizard.py         o guia interativo (5 perguntas → arquivo válido)
harness/sanitizar.py     o DLP que roda antes de qualquer envio
exemplos/                5 áreas com material pronto
docs/                    o método explicado
templates/               o prompt para colar no agente
```

---

## Licença

MIT — use, adapte, distribua. Veja [LICENSE](LICENSE).
