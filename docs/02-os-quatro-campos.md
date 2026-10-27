# Os quatro campos (e por que o agente para sem eles)

## O teste que revelou isso

Material entregue a um agente, sem escopo e sem critério de aceitação. A resposta:

> *"Sem escopo e sem critério de aceitação, o card raiz viraria 8 cards sem como
> verificar conclusão. E o perfil não improvisa em cima de escopo ambíguo."*

Ele **parou**. Não inventou, não "deu um jeito". E estava certo.

---

## Os quatro campos

### 1. OBJETIVO
O que a documentação precisa entregar, em **uma frase**.

❌ "documentar o pentest"
✅ "documentar a técnica executada para que seja reproduzível e defensável"

A segunda versão diz **para quê**. É o que permite a IA decidir o que incluir e o que cortar.

### 2. ESCOPO
O limite explícito. `DENTRO` e `FORA`.

❌ "testar o servidor"
✅ "DENTRO: dev.local:8080. FORA: persistência, dump de credencial, produção."

O `FORA` é mais importante que o `DENTRO`. Sem ele, a IA não sabe onde parar.
e em segurança, isso é risco contratual.

### 3. ETAPAS (numeradas)
Os passos, em ordem. **É o que vira card no Kanban.**

Cada etapa numerada permite ao agente distribuir o trabalho e mostrar o andamento.
Etapa sem número vira uma tarefa só, e você perde a visão do todo.

### 4. CRITÉRIO DE ACEITAÇÃO
Como saber que a nota ficou completa.

❌ "nota boa sobre a técnica"
✅ "nota com comando exato, saída obtida, o privilégio que permitiu a escalação,
mapeamento ATT&CK com sub-técnica, detecção e mitigação"

Sem isso, **nada termina**. O agente não tem como declarar concluído. E não deve.

---

## O mesmo template em qualquer área

| Campo | Red team | Dev | Infra | Jurídico |
|---|---|---|---|---|
| OBJETIVO | técnica com ATT&CK | decisão de arquitetura | mudança com rollback | tese com fundamento |
| ESCOPO | hosts e janela | módulos afetados | ambientes | prazo, instância, partes |
| ETAPAS | recon → acesso → pivô | análise → dev → teste | diagnóstico → mudança | fatos → provas → tese |
| CRITÉRIO | comando + ATT&CK | ADR com alternativas | serviço de pé + rollback | cada pedido com prova |

**O campo muda de nome. A estrutura não muda.**

---

## O que acontece quando falta cada um

| Falta | O agente faz | Você perde |
|---|---|---|
| Critério de aceitação | recusa e lista o que falta | nada, ele te protege |
| Escopo | pergunta, ou para | tempo; em segurança, risco |
| Etapas numeradas | agrupa num card só | a visão distribuída |
| "Não testado" | não consegue inventar | a lista que evita susto |

---

## A regra prática

> Se você não consegue escrever o **critério de aceitação**, o material ainda não está pronto.

Escrever o critério é o que força você a saber o que queria.
