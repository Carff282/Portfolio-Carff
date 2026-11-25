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

## Formato
Carrossel de 6 a 8 slides via `python3 posts/_gerador/gerar.py conteudo.json posts/AAAA-MM-DD-slug/`.
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
3. Windsor.ai, conector instagram, conta 17841458125602140, ação create_carousel_post com image_urls em ordem + caption.
4. Pegar o permalink (get_data: media_id, media_permalink, last_3dT) e atualizar a linha do histórico.
