# Roteiro do post diário do @carffcode

Perfil: "Carff's Cryptic Codes" (@carffcode). O Filipe é dev JavaScript e mexe com ferramentas de IA. Bio: "Do caos ao código". Hashtag da marca: #CodeYourFuture.
Público: devs brasileiros, a maioria com 25 a 34 anos.

## REGRA Nº 1: não pode parecer feito por IA
O Filipe NÃO quer que os posts pareçam gerados por IA. Eles têm que soar como um dev real falando com outros devs.

Texto (slides e legenda):
- Primeira pessoa, como o Filipe falaria: "eu apanhei disso por meses", "aprendi isso num bug em produção", "confesso que demorei pra entender".
- Português falado de dev brasileiro: "pra", "tá", "bora", "kkk" de vez em quando, gírias de dev ("deu ruim", "subir pra produção", "gambiarra"). Sem exagerar.
- PROIBIDO: travessão (—), listas com emojis numerados (1️⃣ 2️⃣), "Neste post", "Vamos explorar", "mergulhar", "desvendar", "no mundo da programação", "é fundamental", "além disso", "em resumo", "Descubra", títulos com dois-pontos no estilo "X: o guia definitivo", frases motivacionais genéricas.
- Varie a estrutura: nem todo post precisa de "5 passos". Às vezes 3 dicas, às vezes uma história de um erro, às vezes "isso vs aquilo", às vezes um único snippet bem explicado.
- Imperfeição faz parte: frases curtas, uma opinião forte, uma piada leve.

Legenda:
- Começa com uma frase pessoal ou uma opinião ("Vou ser sincero: eu usava forEach com async e não entendia por que nada esperava."), não com um gancho de marketing.
- De 3 a 8 linhas, em parágrafos curtos, como alguém digitando no celular. Uma pergunta de verdade no fim para puxar comentário.
- No máximo 2 ou 3 emojis no texto todo, e às vezes nenhum.
- De 3 a 5 hashtags no final (não 10), sempre incluindo #CodeYourFuture.
- Varie o tamanho e o formato de um dia para o outro.

Visual (gerar.py):
- Alterne o "estilo" do JSON: em dias pares do mês "caderno", em dias ímpares "escuro".
- Use os toques à mão em 2 a 4 slides por post (não em todos):
  - "marcar": marca-texto numa palavra-chave do título;
  - "nota": anotação à mão no espaço livre, curta e pessoal ("isso cai em entrevista", "eu errei isso por anos");
  - "circular": círculo à mão no item mais importante.
  A "nota" só aparece se sobrar espaço embaixo. Funciona melhor em slides do tipo pilha, destaque e codigo com poucos checks.
- O kicker da capa pode ser pessoal ("// eu demorei pra entender isso") em vez de técnico.

## Rodízio de temas (pelo dia da semana, horário de Brasília)
- Segunda: arquitetura e design de sistemas
- Terça: dicas de JavaScript / TypeScript
- Quarta: ferramentas de IA para devs
- Quinta: carreira dev (estudos, portfólio, entrevistas, primeiro emprego)
- Sexta: boas práticas (clean code, Git, testes, debugging)
- Sábado: JavaScript na prática (um snippet útil explicado)
- Domingo: IA ou carreira, num tom mais leve e pessoal

Nunca repita um tema que já esteja em posts/historico.md. Prefira temas específicos e úteis a temas genéricos. O conteúdo técnico tem que estar correto.

## Formato do feed (alternar)
- Segunda, quarta, sexta e domingo: CARROSSEL (create_carousel_post com os NN.jpg).
- Terça, quinta e sábado: REEL. Gere os slides normalmente (5 a 7 slides funcionam melhor) e depois
  `python3 posts/_gerador/midia.py reel <pasta>` → <pasta>/reel.mp4 (cerca de 4 s por slide, 9:16).
  Publique com create_video_post (video_url = URL do reel.mp4, caption, share_to_feed true, thumb_offset 0).
  No reel, o texto de cada slide precisa ser lido em uns 4 s: seja ainda mais curto.

## Stories (todo dia)
Gere junto com os slides, ANTES do commit: `python3 posts/_gerador/midia.py story <pasta>` → <pasta>/story.jpg.
Publique com create_story (image_url) logo depois do post do feed. Story não tem legenda.

## Slides
Gere com `python3 posts/_gerador/gerar.py conteudo.json posts/AAAA-MM-DD-slug/ /tmp/preview.jpg`, de 6 a 8 slides (5 a 7 no Reel).
- Slide 1: tipo "capa".
- Miolo: misture os tipos colunas, pilha, codigo, grade e destaque. Use "passo": N e kicker "NN · TÍTULO" quando fizer sentido.
- Último slide: tipo "fechamento", com resumo e um CTA escrito de um jeito pessoal.
- Textos curtos. Código com no máximo ~10 linhas e ~45 caracteres por linha.
- Antes de publicar, abra a prévia e confira se nada está cortado ou sobreposto, e se a anotação à mão apareceu onde devia.

## Publicação
1. Commit da pasta do post (slides + story.jpg + reel.mp4 quando houver) + linha nova em posts/historico.md, push em main.
2. Aguardar o GitHub Pages (~2 min). URL: https://carff282.github.io/Portfolio-Carff/<pasta>/<arquivo>
3. Windsor.ai, conector instagram, conta 17841458125602140: create_carousel_post (image_urls em ordem + caption) ou create_video_post (reel), conforme o dia.
4. Publicar o story (create_story com a URL do story.jpg).
5. Pegar o permalink (get_data: media_id, media_permalink, last_3dT) e atualizar a linha do histórico.
