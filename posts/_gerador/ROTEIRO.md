# Roteiro do post diário do @carffcode

Perfil: "Carff's Cryptic Codes" (@carffcode), dev JavaScript e ferramentas de IA, bio "Do caos ao código", hashtag da marca #CodeYourFuture.
Público: devs brasileiros, majoritariamente 25–34 anos. Tom: direto, prático, informal ("salva pra consultar depois"), português do Brasil.

## Rodízio de temas (pelo dia da semana, horário de Brasília)
- Segunda: Arquitetura e design de sistemas
- Terça: Dicas de JavaScript / TypeScript
- Quarta: Ferramentas de IA para devs
- Quinta: Carreira dev (estudos, portfólio, entrevistas, primeiro emprego)
- Sexta: Boas práticas (clean code, Git, testes, debugging)
- Sábado: JavaScript na prática (um snippet útil explicado)
- Domingo: IA ou carreira, leve e inspirador

Nunca repetir um tema que já esteja em posts/historico.md. Preferir temas específicos e úteis ("5 métodos de array que todo dev deveria saber") a temas genéricos ("o que é JavaScript").

## Formato do feed (alternar)
- Segunda, quarta, sexta e domingo: CARROSSEL (create_carousel_post com os NN.jpg).
- Terça, quinta e sábado: REEL. Gere os slides normalmente (5 a 7 slides funcionam melhor) e depois
  `python3 posts/_gerador/midia.py reel <pasta>` → <pasta>/reel.mp4 (~4 s por slide, 9:16).
  Publique com create_video_post (video_url = URL do reel.mp4, caption, share_to_feed true, thumb_offset 0).
  No reel, o texto de cada slide precisa ser lido em ~4 s: seja ainda mais curto.

## Stories (todo dia)
Gere junto com os slides, ANTES do commit: `python3 posts/_gerador/midia.py story <pasta>` → <pasta>/story.jpg.
Publique com create_story (image_url) logo depois do post do feed. Story não tem legenda.

## Slides
Gere com `python3 posts/_gerador/gerar.py conteudo.json posts/AAAA-MM-DD-slug/`, 6 a 8 slides via `python3 posts/_gerador/gerar.py conteudo.json posts/AAAA-MM-DD-slug/`.
- Slide 1: tipo "capa" (gancho forte + chips opcionais).
- Miolo: misture os tipos colunas, pilha, codigo, grade, destaque. Use "passo": N e kicker "NN · TÍTULO".
- Último: tipo "fechamento" com resumo + CTA (salvar + pergunta para comentar).
- Textos curtos. Código: no máximo ~10 linhas e ~45 caracteres por linha. Conteúdo tecnicamente correto.
- Antes de publicar, abra a imagem de prévia e confira se nada está cortado ou sobreposto.

## Legenda
Gancho na 1ª linha, 3 a 6 linhas de valor com emojis numerados, CTA (salvar + pergunta), 6 a 10 hashtags relevantes, sempre incluindo #CodeYourFuture. Máx. 2.200 caracteres.

## Publicação
1. Commit da pasta do post + linha nova em posts/historico.md, push em main.
2. Aguardar o GitHub Pages (~2 min). URL: https://carff282.github.io/Portfolio-Carff/<pasta>/01.jpg
3. Windsor.ai, conector instagram, conta 17841458125602140: create_carousel_post (image_urls em ordem + caption) ou create_video_post (reel), conforme o dia.
4. Publicar o story (create_story com a URL do story.jpg).
5. Pegar o permalink (get_data: media_id, media_permalink, last_3dT) e atualizar a linha do histórico.
