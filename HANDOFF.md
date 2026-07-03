# HANDOFF — Projeto Spamireza (Campeonato Interno)

> Documento de continuidade. Carregue isto no início de uma nova task para retomar o projeto sem perder contexto.
> Última atualização: 02/07/2026.

---

## 1. Visão geral do projeto

Sistema de **campeonato interno** para a família de clãs **Spamireza** no Clash of Clans (~98 jogadores em 5 clãs). O objetivo é acabar com o remanejo "no achismo" entre os clãs, usando **desempenho real** por liga para decidir quem sobe e quem desce.

**Clãs (ordem = do mais forte ao mais fraco):**
1. SpamiReza
2. RezaSpamandu
3. ScamiReza
4. RezaScamandu
5. e-SpamiReza

Os "principais" jogam do clã 1 ao 5. Em dia de liga, remanejar jogadores entre clãs gera atrito — o ranking resolve isso com critério objetivo.

---

## 2. Modelo de pontuação (já definido e aprovado)

**Princípio central:** medir por **eficiência (por ataque)**, nunca por total acumulado. Isso torna justa a comparação entre quem joga muito e quem joga pouco, e resolve o caso da substituição.

**Índice Spamireza (0–100)** — decide subir/descer:
- **Ataque 55%** = (média de estrelas por ataque ÷ 3) × 100
- **Defesa 20%** = (1 − estrelas sofridas por defesa ÷ 3) × 100
- **Confiabilidade 25%** = ataques feitos ÷ oportunidades reais × 100
- **× Multiplicador de liga** (Champion 1.0, ligas inferiores valem menos — decisão do usuário: SIM, usar multiplicador)
- **Piso de elegibilidade:** mínimo 3 ataques + média móvel das últimas 3 ligas para movimentar

**Regras da substituição (o "coração" do sistema):**
- **Substituído antes de atacar** → não conta como oportunidade (neutro). Não pune.
- **Escalado, ficou na line e não atacou** → falta cheia (derruba a confiabilidade).
- Nota de ataque é sempre média → quem foi tirado após um ataque ruim não é punido duplamente.

**MVP (troféu da temporada):** maior (estrelas de ataque + estrelas negadas na defesa) na liga.

**Pesos escolhidos:** 55/20/25 (eficiência manda). Config editável na planilha.

---

## 3. Arquivos na pasta `Spamireza/`

- **`index.html`** — dashboard principal (o que vai pro GitHub Pages). ATUALMENTE no modo "escalação da liga" (rosters, sem stats ainda). Logo negativa embutida em base64 no topo.
- **`Dashboard_Spamireza.html`** — cópia idêntica do index.html (backup/local).
- **`Indice_Spamireza.xlsx`** — planilha-motor. Abas: Início, Config, Jogadores (98 cadastrados c/ coluna Escalado), Dados (vazia), Ranking Geral. Fórmulas com ZERO erros (validado via recalc).
- **`Indice_Spamireza_EXEMPLO.xlsx`** — versão com dados de exemplo (referência de como fica com stats).
- **`LOGO NEGATIVA`** (PNG sem extensão, 249×308, branca) — usada no dashboard.
- **`LOGO BLACK.png`** — versão preta da logo (não usada ainda).
- **`LIGAS/LIGA DE JULHO:26/`** — prints originais por clã (LISTA PARTICIPANTES + VILAS ESCALADAS). Clã 5 está vazio.
- **`REFERÊNCIAS/`** — vazia.

---

## 4. GitHub / publicação

- **Repositório:** https://github.com/one-lippe/spamireza (público)
- **Site no ar (GitHub Pages):** https://one-lippe.github.io/spamireza/
- **Branch:** main · Pages servindo `index.html` da raiz.
Push feito via git a partir de checkout temporário (a pasta local do Mac não permite operações de git — ver seção 10). Token de acesso pessoal NÃO deve ser salvo em texto puro neste arquivo (GitHub push protection bloqueia e é risco de segurança).


---

## 5. Dados da LIGA DE JULHO/26 (já extraídos e cruzados — 100% conferido)

Guerra em **Dia de Preparação** quando os prints foram tirados (0 ataques). Cruzamento VILAS ESCALADAS × LISTA PARTICIPANTES feito. **Usar os nicks EXATAMENTE como abaixo.**

### Clã 1 — SpamiReza · vs ÄVÈÑGÈRS 2.0 · guerra 15x15
**Escalados (ordem de posição):** Marinaul war, SR · Giovanelli, SR · Jon Snow 2, tozim, Henrique Nerath, KingOfBilada™, SR · Caiçara, Jan, Levi_Neiva, SR · Thiago, Nesk, MAJOR FIV3, Reikan, linch, GENERAL ZOD
**Reservas:** SR · InTheDark☆, LUMINOUS

### Clã 2 — RezaSpamandu · vs حكحكأيهم · guerra 15x15
**Escalados:** SR · Jon Snow, Tony D. Chopper, SrNunes, IGRIS™, ×Darkøn×, GSAzevedo30, LEANDRO, LSWRTH, Neskau, SR . João V., TomorrowBr, SR · Edu, SR·GOD kratos, MAJOR FIV3, PaiDeFamilia
**Reservas:** menolli, Nathan♣, SR · Camburi

### Clã 3 — ScamiReza · vs MINNESOTA · guerra 30x30
**Escalados:** Sene, Agnes, MattosxP, ☆VILA DO PX ッ, Samuel Soares, SR · Pbalestra, KingMpg, nogz, nonick, Psico 2k25, Maxpaz, ROBERTHWILLIAMM, chaos, SR · The off, rei do crime, matias?, Dalton, SR · Nitzuほうめ, SR · Balestra, ·Holtser Ω, SR · DuMAR, SR · GPM 2, RAKAN, SR · One☆, Duff, $ GUADIADOR $, nathan_GO$, ayumatsui, Elianin?, F4KER
**Reservas:** irmão do jorel, Gameplay

### Clã 4 — RezaScamandu · vs THE Clasher · guerra 30x30
**Escalados:** Lider Andre, Deyvidzk, SR·Dos Ovos, Lider André 2, SR · Dennis, LigeirinhOxD, CoR1nG4 ×.×, Lider André 3, Fernandes^, NAUZIN, Nesk', BELLION™, BERU炎, h7dek1, Ghostface, Ganso, Jan™, PaulinhoPH, Nathan TH11, SR · Chefex, SR · JotaErre, RAGNAROK, Honrado, -Meliodas-, °DAxiLHA°, Tomorrowland, ☆InTheDark☆, JigSaw, Ligeirinh2xD, GSAzevedo30 #2
**Reservas:** SR · Borges

### Clã 5 — e-SpamiReza
Sem imagens ainda (pasta vazia). Aba fica **travada 🔒** no dashboard.

**Totais:** 98 vilas (15+2, 15+3, 30+2, 30+1 por clã).

---

## 6. Observações importantes de dados

- **MAJOR FIV3 = DUAS CONTAS diferentes** (mesmo nick), uma no clã 1 e outra no clã 2. Ambas válidas, cada uma no seu clã. NÃO é conflito.
- **Nicks repetidos entre clãs são contas diferentes** — manter exatamente como estão: Nesk (c1) / Neskau (c2) / Nesk' (c4); os três "Lider André" (Lider Andre, Lider André 2, Lider André 3); GSAzevedo30 (c2) e GSAzevedo30 #2 (c4); Jan (c1) e Jan™ (c4); Nathan♣ (c2) / nathan_GO$ (c3) / Nathan TH11 (c4).
- Clãs 1 e 2 são guerra 15x15; clãs 3 e 4 são 30x30.

---

## 7. Estado atual do dashboard (`index.html`)

- Modo "escalação": abas dos clãs 1–4 clicáveis, clã 5 travada 🔒.
- Cada clã mostra: adversário, tamanho da guerra, contagem escalados/reservas, lista de escalados em ordem de posição + reservas separados por divisória.
- Tema azul-escuro Spamireza. **Logo negativa** (branca) no topo em base64, no lugar do antigo ícone ⚔️. Texto "SPAMIREZA" removido do título (a logo já traz o nome).
- Ainda NÃO tem estatísticas (liga não jogou). Quando as guerras rolarem, o dashboard deve migrar para o modo "ranking" (Índice, MVP, zonas de promoção/rebaixamento) — o EXEMPLO.xlsx e a versão anterior do dashboard mostram como esse modo fica.

---

## 8. Pendências / próximos passos (o usuário quer "correções pontuais")

- [ ] Correções pontuais no dashboard (o usuário vai detalhar na nova task).
- [ ] Clã 5 (e-SpamiReza): faltam os prints de LISTA PARTICIPANTES e VILAS ESCALADAS.
- [ ] Quando a 1ª guerra terminar: coletar desempenho por jogador (estrelas, % destruição, defesa, ataques usados, substituições) e alimentar a aba **Dados** da planilha → o Índice/MVP/zonas calculam sozinhos.
- [ ] Definir a liga real de cada clã nesta temporada na aba **Config** (afeta o multiplicador).
- [ ] Possível automação da coleta via API oficial do Supercell / ClashKing / CWStats (evita printar 98 jogadores manualmente) — ver telas participantes só têm o nome; substituição precisa ser marcada à mão.
- [ ] Textos prontos para o grupo (versão colíderes) já foram redigidos em conversa anterior — reaproveitar se precisar.

---

## 9. Preferências de trabalho

- Usuário: Lippe (One Publicidade). Prefere respostas concisas e diretas.
- Projeto recreativo. Conta do GitHub é de teste.
- Sempre publicar/verificar o dashboard no ar após mudanças.

---

## 10. Git / push — como funciona de verdade (02/07/2026)

- A pasta `Spamireza/` no Mac **não permite deletar/renomear arquivos** (restrição do Cowork nessa pasta conectada). Git precisa criar/apagar arquivos temporários (`.git/objects/tmp_*`, locks) o tempo todo — por isso `git init`/`git push` rodado direto nela **sempre falha** com "Operation not permitted".
- Por isso todo o histórico do repo até aqui era só commits "Add files via upload" (feitos manualmente pelo site do GitHub).
- **Forma que funciona:** clonar o repo num diretório temporário do sandbox, copiar os arquivos atualizados da pasta local pra lá, commitar e dar push de lá. Arquivo de referência de token de acesso: pedir para o usuário fornecer de novo caso necessário (não guardar em texto puro em arquivos deste repositório — GitHub bloqueia por push protection e é risco de segurança).
- Repo público já contém (após push de 02/07/26): index.html, README.md, ARTES/, Dashboard_Spamireza.html, Indice_Spamireza.xlsx, Indice_Spamireza_EXEMPLO.xlsx, LOGO BLACK.png, LOGO NEGATIVA, LIGAS/ (prints das escalações), HANDOFF.md.
