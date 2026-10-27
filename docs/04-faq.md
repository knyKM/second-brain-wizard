# Perguntas frequentes

## "Meu agente recusou o material. O que houve?"

Falta um dos quatro campos. O wizard valida:

```bash
python wizard/wizard.py --check seu-arquivo.txt
```

Ele diz **qual** campo falta e por quê. Normalmente é critério de aceitação.

## "A IA inventou informação que não estava na minha anotação"

Três defesas, em ordem:

1. No prompt: *"NÃO invente nada que não esteja nas anotações"*
2. No prompt: *"o que completar com conhecimento próprio, marque como INFERIDO"*
3. No material: inclua a seção **"O QUE EU NÃO TESTEI"**, que dá à IA um lugar
   legítimo para colocar o que não sabe, em vez de preencher com suposição

## "Preciso usar Obsidian?"

Não. O material gerado é texto puro. Funciona com Notion, Logseq, pasta com git,
ou até uma pasta de arquivos `.md` que você abre no editor.

O que importa é ser **pesquisável** e permitir **ligação entre notas**.

## "Funciona com ChatGPT / Claude / modelo local?"

Sim. O formato dos quatro campos é universal. É o que qualquer agente precisa
para não travar. O harness também é independente de provedor.

Se você usa perfil local, atenção: **mesmo local, o prompt sai para a API do
provedor**. A sanitização continua obrigatória.

## "Quanto tempo leva para configurar?"

O wizard: 5 minutos para o primeiro material.
O hábito: uma semana até virar automático.

Comece com **uma coisa que você repete toda semana**.

## "E se meu material não tiver nada sensível?"

O harness vai reportar zero marcadores, e isso é o comportamento correto.
Não force match. Material bem escrito (senha no gerenciador, IP sintético)
não tem o que mascarar.

## "Posso adaptar para a minha área?"

Sim, é o propósito. Adicione sua área em `AREAS` no `wizard/wizard.py`:

```python
"minha-area": {
    "nome": "Nome da área",
    "objetivo": "o que a documentação precisa entregar",
    "fora": "o que fica de fora por padrão",
    "etapas": [("Etapa 1", "o que acontece"), ...],
    "criterio": "como saber que ficou completo",
},
```

Aceitamos contribuição. Abra um PR com a sua área.

## "Por que o agente às vezes cria cards demais?"

Se você usa orquestração com Kanban, um playbook de 7 etapas vira 7 cards.
e o orquestrador pode subdividir cada um. **Isso é o sistema funcionando**: ele
mostra o trabalho distribuído.

Se estiver demais, reduza as etapas no material. Menos etapas = menos cards.

## "Qual a diferença entre este repo e um prompt qualquer?"

Um prompt qualquer resolve **uma vez**. Este repositório resolve o **processo**:

- o wizard garante que o material esteja no formato certo
- o harness garante que dado sensível não vaze
- o validador diz o que falta antes de você perder tempo
- os 5 exemplos mostram como é em cada área

O prompt é a última milha. O valor está em chegar até ele sem erro.

## "Isso é seguro para material de cliente?"

Com o harness rodando: o dado sensível não sai da máquina, o modelo vê marcadores.

**Mas leia os limites:** o harness não adivinha e ausência de match não é prova.
Em ambiente com exigência de compliance, some isso a uma política de retenção
por escrito e revisão humana antes do envio.

O harness é uma camada, não uma garantia jurídica.
