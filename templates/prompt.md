# Template de prompt para o agente

Copie, substitua `<...>` e cole junto com o arquivo **sanitizado**.

---

## Versão completa (recomendada)

```text
@file:<caminho>/<projeto>.sanitizado.txt

Estas são minhas anotações cruas sobre <o que foi feito>.

Documenta no meu acervo, no projeto "<NOME DO PROJETO>", organizando tudo:

1. O que foi feito, em ordem.
2. O que foi descoberto ou decidido, com a evidência que sustenta cada ponto.
3. O que ficou em aberto e o que falta para fechar.
4. As dúvidas que eu registrei — sem inventar resposta.
5. As lições que servem para a próxima vez.

Regras:
- NÃO invente nada que não esteja nas anotações.
- O que você completar com conhecimento próprio marca como INFERIDO, nunca CONFIRMADO.
- Se faltar informação para algum item, registra a lacuna em vez de preencher.
- Cria o índice do projeto e liga as notas com wikilinks.
- Se encontrar credencial, segredo ou dado sensível: registra existência e local,
  mascara o valor como <REDACTED> e me avisa. Nunca copia o valor.
```

## Versão com Kanban (trabalho distribuído)

```text
Documenta as etapas como cards no Kanban, para eu ver o trabalho distribuído.
Cada card só fecha com o artefato descrito no critério de aceitação.
Se um card falhar duas vezes, para e reporta o erro real em vez de contornar.
```

## Versão mínima (quando você confia no material)

```text
@file:<arquivo>.sanitizado.txt

Documenta isso no projeto "<NOME>".
Aplica a regra: nada inventado, lacuna registrada, valor sensível mascarado.
```

---

## O que cada regra evita

| Regra | Evita |
|---|---|
| "não invente nada" | alucinação apresentada como fato |
| "marque como INFERIDO" | inferência virando verdade no relatório |
| "registra a lacuna" | preenchimento com suposição plausível |
| "mascara o valor" | vazamento em nota persistente |
| "cada card fecha com artefato" | card marcado como pronto sem entrega |

---

## Depois de rodar, verifique

```bash
# o arquivo existe mesmo?
ls -la "<pasta do projeto>/"

# o agente citou o caminho do artefato?
# se ele disse "terminei" sem citar arquivo, não terminou
```

> **Regra de ouro:** agente que diz "terminei" não é prova.
> A tarefa só fecha com o artefato descrito.
