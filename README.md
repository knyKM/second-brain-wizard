# Segundo Cérebro

Um wizard que configura o seu. Você responde cinco perguntas e sai com o material pronto
para uma IA organizar.

Não é sobre segurança. Serve para desenvolvimento, infraestrutura, jurídico, análise de
dados, pesquisa, operação. Qualquer trabalho em que você resolve um problema difícil e
depois esquece como resolveu.

## O problema

Você resolve algo que dá trabalho. Anota no bloco de notas, no chat, num print. Três meses
depois o mesmo problema aparece e você recomeça do zero.

Não é falta de disciplina. Registrar dá trabalho na hora e o benefício só aparece depois.
Quem paga a conta é o você do futuro.

E tem um agravante. Quem trabalha com segurança, ou desenvolvimento, ou jurídico, produz
muito conhecimento e retém pouco. O gargalo nunca foi produzir. Sempre foi reter.

## Como funciona

São três passos.

Você captura do jeito que sair. Sem formato, sem se preocupar com nada. Se você exigir
formato na hora da captura, você não captura.

A IA estrutura. Ela pega a anotação feia e devolve uma nota com forma fixa. Formato é o que
permite achar depois, e formato não é trabalho seu.

Na próxima vez você reutiliza. Busca antes de começar em vez de recomeçar.

## Começando

```bash
git clone https://github.com/knyKM/second-brain-wizard.git
cd second-brain-wizard

# 1. o wizard pergunta cinco coisas e gera seu material
python wizard/wizard.py

# 2. o harness protege dado sensível antes de mandar para a IA
python harness/sanitizar.py meu-projeto.txt --revisar

# 3. mande o arquivo .sanitizado.txt para a IA
```

Precisa de Python 3.9 ou mais novo. Nada além disso.

## Por que um wizard e não um template

Porque todo mundo comete o mesmo erro: entrega material vago para a IA e espera que ela dê
um jeito.

Ela não dá. Um agente sério para e diz o que falta. Isso é bom, não é defeito. A resposta
que eu recebi quando testei isso pela primeira vez:

> "Sem escopo e sem critério de aceitação, o card raiz viraria 8 cards sem como verificar
> conclusão. E o perfil não improvisa em cima de escopo ambíguo."

O wizard existe para você não passar por isso. Ele pergunta as quatro coisas que a IA precisa:

```
## OBJETIVO              o que a documentação tem que entregar
## ESCOPO               DENTRO: ...  /  FORA: ...   (o limite impede invenção)
## ETAPAS               numeradas, porque é o que vira card no Kanban
## CRITERIO DE ACEITACAO como saber que acabou
```

Se você não consegue escrever o critério de aceitação, o material ainda não está pronto.
Escrever o critério é o que força você a saber o que queria.

## O harness

Essa é a parte que quase todo mundo esquece.

Quando você manda anotação crua para uma API de modelo, ela sai da sua máquina. Se tiver
senha, token, CPF ou nome de cliente, você acabou de vazar. E não tem como desfazer.

Então o dado sensível não atravessa a fronteira da máquina. O fluxo fica assim:

```
anotação crua
      |
      v
[ HARNESS ]  roda local, antes de qualquer envio
      |
  +---+---+
  v       v
versão   mapa local
limpa    (fica na máquina)
  |
  v
 MODELO  (só vê <<CREDENCIAL_2>>, nunca a senha)
```

O modelo recebe `<<CREDENCIAL_2>>` e escreve "havia uma credencial no arquivo de
configuração". Que é toda a informação de que ele precisa.

```bash
python harness/sanitizar.py anotacoes.txt --revisar
```

Ele mascara credencial nomeada (`senha:`, `password=`, `api_key:`, `token:`), tokens
conhecidos (`sk-...`, `ghp_...`, `glpat-...`, `AKIA...`, `xoxb-...`, JWT), bloco de chave
privada inteiro, a parte `Password=` de connection string (preservando server e database),
e-mail, telefone, CPF, CNPJ, IP privado e público, e domínio de cliente.

Dois limites que você precisa saber. Ele não adivinha, então padrão fora da lista passa
adiante (é por isso que existe o `--revisar`). E ausência de match não é prova de segurança:
"nenhum padrão encontrado" quer dizer "nada que eu conheça", não "está tudo bem".

O arquivo `*.mapa-local.json` tem os valores reais para você poder reverter. É o arquivo
mais perigoso do processo. Nunca em repositório, chat ou nuvem.

## Áreas com exemplo pronto

```bash
python wizard/wizard.py --areas
```

Servem para você não começar do zero:

- `red-team` documenta a técnica com ATT&CK, detecção e mitigação
- `desenvolvimento` registra a decisão de arquitetura com as alternativas descartadas
- `infraestrutura` registra a mudança com rollback testado
- `juridico` organiza fatos, provas e tese sem alegar o que não tem prova
- `dados` deixa a análise reproduzível por outra pessoa

Os cinco exemplos estão em `exemplos/`.

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

RESULTADO: material valido.
```

Se faltar campo ele diz qual, e diz o que vai acontecer: o agente vai parar e pedir.

## O que fazer com o material

O arquivo gerado é a entrada. A saída é a nota estruturada no seu acervo, seja Obsidian,
Notion, Logseq ou uma pasta qualquer com git.

Prompt para colar junto com o arquivo sanitizado:

```text
@file:<arquivo>.sanitizado.txt

Estas são minhas anotações cruas sobre este trabalho.

Documenta no meu acervo, no projeto "<NOME>":

- o que foi feito, em ordem
- o que foi descoberto ou decidido, com a evidência que sustenta cada ponto
- o que ficou em aberto e o que falta para fechar
- as dúvidas que eu registrei, sem inventar resposta
- as lições que servem para a próxima vez

Regras:
1. NÃO invente nada que não esteja nas anotações.
2. O que completar com conhecimento próprio marca como INFERIDO, nunca CONFIRMADO.
3. Se faltar informação, registra a lacuna em vez de preencher.
4. Cria o índice e liga as notas com wikilinks.
5. Credencial ou segredo: registra existência e local, mascara o valor, me avisa.
```

## O que faz isso funcionar

Agente que aceita material vago produz documento bonito e vazio. Agente que para e diz o
que falta está trabalhando para você. Aprenda a gostar da recusa.

Separe fato de hipótese. Confirmado, inferido e não testado são três estados, não dois.

Registre o que você não testou. Vale mais do que a lista do que testou.

O valor mora na ligação entre as notas. Uma nota sozinha é um arquivo. Duas notas ligadas
são conhecimento.

E comece pequeno. Uma coisa que você repete toda semana. Escreve o passo a passo uma vez e
pronto, você já tem um playbook.

## O teste que quase ninguém faz

Abra sua própria nota de seis meses atrás.

Você consegue executar o que está escrito, sem pensar?

Se a resposta for "quase", você acabou de encontrar o seu problema. Documentação não falha
quando você escreve. Falha quando outra pessoa, ou você no futuro, tenta usar.

## O que tem aqui dentro

```
wizard/wizard.py         o guia interativo (cinco perguntas, um arquivo válido)
harness/sanitizar.py     o filtro que roda antes de qualquer envio
exemplos/                cinco áreas com material pronto
docs/                    o método explicado com calma
templates/               o prompt para colar no agente
```

## Licença

MIT. Use, adapte, distribua. O arquivo LICENSE tem o texto.
