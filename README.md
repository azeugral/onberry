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

- **Marca:** um mirtilo visto de cima, com a coroa de 5 sépalas aberta em vista 3/4. O nome "On Berry" está em Newsreader convertido em curvas. Tudo é gerado por `tools/logo.py`, em `assets/logo/`:
  - `logo-clara.svg` e `logo-escura.svg`: com o subtítulo "Vale do São Francisco";
  - `*-simples.svg`: só a marca e o nome;
  - `marca-*.svg`: só o símbolo.
- **Favicon:** `favicon.svg`, mais os PNG de 32, 192 e 512 e o `apple-touch-icon.png` (gerados por `tools/processar.py icones`).

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

As fotos são reais, do Instagram da marca (originais em `../_ref/ig`), recortadas por `tools/processar.py fotos`: embalagem de 125 g, flor do mirtilo, plantio em vasos, colheita de uva, parreiral e uvas em bandeja. A resolução é baixa (até 1125 px), então **substituir pelas fotos que o cliente vai enviar**.

## CONFIRMAR com o cliente

Os dados abaixo estão **genéricos ou presumidos** e precisam da versão correta:

- [ ] **WhatsApp comercial:** está como `(00) 00000-0000`.
- [ ] **E-mail:** está como `contato@onberry.com.br`. O domínio `onberry.com` **não é deles**, ele redireciona para outra marca (lontreau.com). Definir o domínio do site.
- [ ] **Cidade e endereço:** hoje aparece só "Vale do São Francisco". Confirmar se é Petrolina (PE), Juazeiro (BA), Lagoa Grande, Casa Nova etc.
- [ ] **Nome da marca:** o Instagram diz "On Berry", a embalagem diz "ON BERRIES" e a foto de perfil, "On-Berry". O site usa **On Berry**.
- [ ] **Uvas:** quais variedades (com ou sem semente, cores) e se a uva é produção própria ou só comercialização. A bio fala em "comercialização de Berrys e Uvas".
- [ ] **Mirtilo:** variedades, área plantada, número de plantas, ano de início e época de safra.
- [ ] **Processo (seção Cultivo):** plantio em vasos e irrigação localizada vêm das fotos. Colheita em várias passadas e refrigeração até a expedição são o padrão do mirtilo; confirmar como eles fazem.
- [ ] **Conservação:** "refrigerado entre 0 e 4 °C" é uma orientação genérica.
- [ ] **Selos da seção A empresa:** confirmar "Produção própria", "Cultivo sustentável" (este está no rótulo) e "Mercado nacional". Exportam?
- [ ] **Certificações:** GlobalG.A.P., orgânico etc., se tiverem, para criar uma faixa de selos.
- [ ] **Logo:** a identidade foi criada do zero (a foto de perfil atual parece gerada por IA). Validar com o cliente.

## Dados regionais usados (públicos, não são da empresa)

- Mais de 3.000 horas de sol por ano no Vale do São Francisco.
- Até 2,5 safras de uva por ano no polo irrigado.
- Latitude de cerca de 9° S (Petrolina/Juazeiro).
- O Vale é o principal polo de uva de mesa do país.

## Ferramentas

| Script | O que faz |
|---|---|
| `tools/mirtilos.py` | cena 3D do hero (Blender) |
| `tools/logo.py` | marca, wordmark e favicon SVG |
| `tools/processar.py` | fotos, hero (MP4/posters), ícones |
| `tools/conferir.py` | prints em 8 aparelhos + auditoria de overflow |

Site por [L R G Z](https://lrgz.com.br).
