# On Berry · site institucional

One page informativa da **On Berry** (@onberrybrasil_), empresa nacional de desenvolvimento agrícola que comercializa berries e uvas do Vale do São Francisco. A versão é de apresentação: não tem venda e está com `noindex`.

- **Publicado em:** https://azeugral.github.io/onberry/
- **Stack:** HTML + CSS + JS puro, sem build.
- **Fontes:** Newsreader (títulos) e Manrope (texto), pelo Google Fonts.

## Identidade

| Cor | Hex | Uso |
|---|---|---|
| Noite | `#0B0C1F` | hero, Vale, rodapé |
| Anil | `#151735` | seção Mirtilo, marca |
| Pruína | `#B9C1DC` | detalhes sobre o escuro (a cera azulada do mirtilo) |
| Creme | `#F4EFE4` | fundo claro, logo sobre o escuro |
| Areia | `#EAE2D1` | seção Uvas |
| Oliva | `#5F6B2C` | chapéus, tirado do rótulo verde da embalagem |
| Ouro | `#C9973F` | detalhes, o sol do selo |

- **Logo OFICIAL do cliente** (arquivo dele, RGBA, em `../_ref/logo-oficial/`), aplicada por `tools/logo_oficial.py`:
  - `assets/logo/oficial-vertical.*`: logo completa, usada no rodapé e na OG;
  - `assets/logo/simbolo.*`: só o símbolo, usado no favicon (`favicon.ico` + PNG de 32/192/512 + apple-touch, sobre o azul-noite da arte oficial);
  - `assets/logo/horizontal-clara.svg` / `horizontal-escura.svg`: versão de leitura para o topo e para textos. É o símbolo oficial + "On-Berry" em Manrope 500 + a folhinha azul da logo.
- A proposta de marca da LRGZ (mirtilo com coroa) foi descartada e está guardada em `../_ref/logo-proposta-lrgz/`.

## Hero (mirtilos caindo)

A cena 3D é renderizada no Blender 5.2 (Cycles) por `tools/mirtilos.py`:

- mirtilos modelados com a coroa e a cera (pruína) irregular, folhas com nervuras, desfoque de câmera, luz quente de sertão e contraluz fria;
- o loop é perfeito: cada objeto percorre um número inteiro de vãos e de voltas a cada 6 s.

```
blender -b -P tools/mirtilos.py -- --modo still   --saida ../_ref/render/still     # 3840x2160
blender -b -P tools/mirtilos.py -- --modo desktop --saida ../_ref/render/desktop   # 1920x1080, 180 quadros
blender -b -P tools/mirtilos.py -- --modo mobile  --saida ../_ref/render/mobile    # 1080x1920, 180 quadros
python tools/processar.py hero                                                     # MP4, posters e imagens 4K
```

No site, o vídeo é escolhido pela orientação da tela (retrato ou paisagem) e só carrega depois do primeiro paint. Ele não carrega com `prefers-reduced-motion` nem com economia de dados, e pausa fora da tela.

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
| `tools/mirtilos.py` | cena 3D do hero (Blender) |
| `tools/logo.py` | marca, wordmark e favicon SVG |
| `tools/processar.py` | fotos, hero (MP4/posters), ícones |
| `tools/conferir.py` | prints em 8 aparelhos + auditoria de overflow |

Site por [L R G Z](https://lrgz.com.br).
