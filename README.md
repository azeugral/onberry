# On Berry · site institucional

One page informativa da **On Berry** (@onberrybrasil_), empresa nacional de desenvolvimento agrícola que comercializa berries e uvas do Vale do São Francisco. A versão é de apresentação: não tem venda e está com `noindex`.

- **Publicado em:** https://azeugral.github.io/onberry/
- **Stack:** HTML + CSS + JS puro, sem build.
- **Fontes:** Saira (títulos) e Manrope (texto), pelo Google Fonts.

## Identidade (hi-tech, derivada da logo oficial)

| Token | Hex | Uso |
|---|---|---|
| Abismo | `#020619` | fundo base |
| Noite | `#050D2E` | seções alternadas, vidro |
| Elétrico | `#2563FF` | botões, faixa Uvas, brilhos |
| Ciano | `#7CD4FF` | rótulos, bordas de luz, gradiente dos títulos |
| Gelo | `#E6F5FF` | texto de destaque |
| Violeta | `#6D4BFF` | halo (como na arte escura da logo) |

- **Tipografia:**
  - **Saira expandida** (eixo `wdth` 112–125, peso 600–800) nos títulos, nos números e nos rótulos em caixa-alta;
  - **Manrope** no texto corrido.
- **Assinatura:** a **estrela de 4 pontas da logo** é o marcador do sistema (chapéus, selos, ícones dos cartões). Os títulos levam um gradiente branco → ciano → azul.
- **Componentes:**
  - botões **chanfrados** (canto cortado), com a seta num módulo próprio e uma faixa de luz no hover;
  - painéis de **vidro** com borda de luz que segue o mouse (só com ponteiro fino);
  - fotos com moldura de gradiente e revelação em clip-path.
- **Hero 3D:** re-iluminado no azul da logo, com contraluz ciano, halo violeta e fundo elétrico. A versão índigo anterior está em `../_ref/render/v1-indigo`.

- **Logo OFICIAL do cliente** (arquivo dele, RGBA, em `../_ref/logo-oficial/`), aplicada por `tools/logo_oficial.py`:
  - `assets/logo/oficial-vertical.*`: logo completa, usada no rodapé e na OG;
  - `assets/logo/simbolo.*`: só o símbolo, usado no favicon (`favicon.ico` + PNG de 32/192/512 + apple-touch, sobre o azul-noite da arte oficial);
  - `assets/logo/horizontal-clara.svg` / `horizontal-escura.svg`: versão de leitura para o topo e para textos. É o símbolo oficial + "On-Berry" em Saira expandida 600 + a folhinha azul da logo.
- A proposta de marca da LRGZ (mirtilo com coroa) foi descartada e está guardada em `../_ref/logo-proposta-lrgz/`.

## Hero (imagem fixa)

O hero usa a **imagem fixa enviada pelo cliente**: mirtilos molhados com folhas, 1938×812 (original em `../_ref/hero-fixo/`).

- **Arquivos:** `assets/img/hero-mirtilos.webp` (1938 px) e `-1300.webp`, escolhidos por `srcset`. Em tela em pé o `sizes` pede a maior, porque a foto aparece ampliada.
- **PC e celular deitado:** a foto ocupa o hero inteiro com `object-position: 56%`, para o mirtilo principal ficar à direita do texto.
- **Tela em pé (celular e tablet):** a foto ocupa os 62% de cima (52% em telas baixas), centrada na fruta (`76%`), e se funde no fundo escuro onde fica o texto. Assim ela não é esticada além da resolução.
- **Animação:** só um fade de entrada; a imagem é estática.
- **Histórico:** antes houve um loop MP4 (`../_ref/render/hero-mp4-eletrico/`) e uma sequência de 120 quadros pela rolagem (protótipo `_prototipos/mirtilos-gotas`). O cliente preferiu a imagem fixa.
- **OG (`assets/img/og.jpg`):** usa a mesma foto com a logo oficial.

## Fotos

As fotos são reais, dos posts da marca de 2026 (originais em `../_ref/ig`), recortadas por `tools/processar.py fotos`: embalagem de 125 g, flor do mirtilo e plantio em vasos. A resolução é baixa (até 1125 px), então **substituir pelas fotos que o cliente vai enviar**.

As fotos de uva (posts de 2019 e 2020) **saíram do site** porque não dá para garantir que sejam deles: a da colheita tem moldura e parece repost ou banco de imagem. Elas estão guardadas em `../_ref/fotos-uva-duvidosas/`.

## Regra do conteúdo: só o comprovado

Desde 26/10, o site só afirma sobre a empresa o que está na **bio do Instagram** e na **embalagem**. Tudo o mais é fato geral da região ou da fruta, escrito como geral.

**Sobre a On-Berry (comprovado):**

- empresa nacional de desenvolvimento agrícola, voltada à comercialização de berries e uvas do Vale do São Francisco (bio);
- a embalagem: mirtilo, cultivo sustentável, produzido no Vale São Francisco, cumbuca de 125 g, rótulo "On Berries · Fresh & Natural";
- plantio de mirtilo em vasos sobre cobertura de solo, e flores e frutos (fotos deles);
- o Instagram @onberrybrasil_.

**Sobre a região e a fruta (fatos públicos):**

- cerca de 3.000 h de sol por ano;
- até 2,5 safras de uva por ano;
- latitude de ~9° S;
- irrigação com água do Rio São Francisco;
- clima seco, com menos doenças fúngicas;
- principal região exportadora de uva de mesa;
- antocianinas, pruína, variedades de baixa exigência de frio, maturação escalonada do mirtilo e lavar só na hora.

**O que saiu:**

- "cultivamos" e "produção própria";
- variedades, irrigação controlada e acompanhamento técnico;
- sabor, colheita manual e conservação entre 0 e 4 °C;
- "uvas colhidas à mão" e "mercado nacional";
- WhatsApp e e-mail placeholder (no contato ficou só o Instagram);
- as fotos de uva.

O hero e a faixa da pruína são **render 3D ilustrativo**, não fotografia da empresa.

## Para acrescentar quando o cliente enviar

- [ ] **WhatsApp comercial e e-mail:** voltam para a lista de canais em `#contato`. O domínio `onberry.com` **não é deles** (redireciona para lontreau.com).
- [ ] **Cidade e endereço:** Petrolina (PE)? Juazeiro (BA)? Outra?
- [ ] **Nome:** Instagram "On Berry", embalagem "ON BERRIES", logo "On-Berry". O site usa **On-Berry**.
- [ ] **Se cultivam** (produção própria) ou só comercializam; área, plantas, variedades e safra.
- [ ] **Uvas:** variedades, origem e fotos próprias.
- [ ] **Processo real:** colheita, seleção, câmara fria.
- [ ] **Certificações** (GlobalG.A.P. etc.) e se exportam.
- [ ] **Logo em vetor:** o arquivo oficial é PNG/WebP (1254 px). Pedir o vetor (SVG/AI/PDF).

## Ferramentas

| Script | O que faz |
|---|---|
| `tools/mirtilos.py` | cena 3D dos mirtilos secos (usada no still da faixa da pruína e na OG) |
| `tools/logo.py` | marca, wordmark e favicon SVG |
| `tools/processar.py` | fotos, hero (MP4/posters), ícones |
| `tools/conferir.py` | prints em 8 aparelhos + auditoria de overflow |

Site por [L R G Z](https://lrgz.com.br).
