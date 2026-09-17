# Desafio QA Agibank - Automação de Testes Web (E2E + POM + CI/CD + Auditoria)

Framework de automação de testes E2E (End-to-End) desenvolvido como solução para o desafio técnico de QA do Agibank. Implementa validações para **4 módulos**: Calculadora de Dias Úteis, Calculadora de Juros Compostos (Abas Dívida / Investimento), Calculadora de Investimentos (POM dedicada, Golden Katalon + Portfolio + BlazeMeter) e a funcionalidade de pesquisa de artigos no Blog do Agi. Inclui **Sistema de Auditoria de Logs com Criptografia Fernet AES-128 (LGPD)**.

---

## 🛠️ Stack Técnica

| Componente          | Tecnologia                          | Versão   |
|---------------------|-------------------------------------|----------|
| Linguagem           | Python                              | 3.11+    |
| Framework de Teste  | Pytest                              | 7.4.x    |
| Automação Web       | Playwright (Chromium)               | 1.40.x   |
| Relatórios          | pytest-html (HTML self-contained)   | 4.1.x    |
| Auditoria de Logs   | SQLite + JSONL + Fernet AES-128     | 43.x     |
| Padrão Arquitetural | Page Object Pattern (POM)           | -        |
| CI/CD               | GitHub Actions (ubuntu-latest)      | -        |
| Cross-Platform      | Windows / Linux / macOS             | -        |

---

## 📁 Estrutura do Projeto

```
desafioagibank/
├── .github/
│   └── workflows/
│       └── e2e-tests.yml                  # Pipeline CI/CD (com JOB SUMMARY de como acessar relatórios)
│
├── pages/                                  # Camada Page Objects (POM)
│   ├── base_page.py                        # Classe base (comum a todas páginas, bypass Cloudflare)
│   ├── calculadora_dias_uteis_page.py      # POM Calculadora Dias Úteis
│   ├── calculadora_juros_page.py           # POM Calculadora Juros Compostos (Aba Dívida Katalon Golden)
│   ├── calculadora_investimentos_page.py   # POM Calculadora de Investimentos (Aba Invest, BlazeMeter, Portfolio)
│   └── blog_agi_page.py                    # POM Pesquisa de Artigos (Blog do Agi)
│
├── reports/
│   ├── auditoria/
│   │   ├── data/                            # Persistência 2 camadas
│   │   │   ├── audit_log.jsonl              # 1. JSONL append-only (1 evento / linha)
│   │   │   ├── audit_log.db                 # 2. SQLite índices para consultas
│   │   │   └── keys/chave_auditoria_fernet.key   # Chave criptografia Fernet (NÃO COMMITADA!)
│   │   ├── auditor_logger.py                # CORE: Enum 5 eventos, criptografia, cadeia custódia SHA-256, DAO
│   │   ├── auditoria_consultar.py           # CLI auditoria (10 flags: --resumo --validar-cadeia --json --top-erros)
│   │   └── auditoria_retencao_lgpd.py       # Retenção LGPD 90 dias (dry-run padrão para segurança)
│   └── .gitkeep
│
├── tests/                                  # Camada de Casos de Teste (Pytest)
│   ├── test_calculadora_dias_uteis.py       # 7 testes Dias Úteis
│   ├── test_calculadora_juros.py            # 8 testes Juros (inclui 1 Golden Katalon 13.419,08)
│   ├── test_calculadora_investimentos.py    # 9 testes Investimentos (1 Golden Portfolio 17.274,56 + BlazeMeter)
│   ├── test_blog_agi_pesquisa.py            # 4 testes Pesquisa Blog Agi
│   └── test_auditoria_relatorios.py         # 7 testes Sistema de Auditoria (cripto, performance, integridade, LGPD)
│
├── conftest.py                             # Fixtures Playwright + 4 hooks Auditoria (sessionstart/teste/exception/unconfigure)
├── requirements.txt                        # Dependências do projeto
├── pytest.ini                              # 25 marcadores pytest + reports/report.html padrão
├── .gitignore                              # Bloqueia 100% dos relatórios (NÃO sobem para Git)
│
├── Caso_1_Gerar_Relatorio_Novo.cmd         # (Windows 2 cliques) CASO 1: Rodar + GERAR relatório
├── Caso_2_Abrir_Relatorio_Existente.cmd    # (Windows 2 cliques) CASO 2: Só ABRIR o último existente
├── Caso_3_Relatorio_Auditoria.cmd          # (Windows 2 cliques) CASO 3: Relatório de Auditoria (quem acessou, erros)
├── rodar_testes_e_gerar_relatorio_novo.ps1
├── abrir_relatorio_existente.ps1
├── relatorio_auditoria_logs.ps1
└── README.md                               # Este arquivo
```

---

## 🚀 Como Configurar e Executar (Passo a Passo)

### Pré-requisitos Obrigatórios
- **Python 3.11 ou superior** instalado em sua máquina (verifique com: `python --version`)
- **Pip** disponível no PATH
- (Opcional) **Git** para clonar o repositório

---

### Passo 1: Clonar / Preparar o Projeto

```bash
git clone https://github.com/bioadsl/desafioagibankweb.git
cd desafioagibank
```

---

### Passo 2: Criar e Ativar Ambiente Virtual

#### 🪟 Windows (PowerShell / CMD)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
# Observação: se ocorrer erro de execução de scripts no PowerShell,
# execute primeiro: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

#### 🐧 Linux / 🍎 macOS (Terminal)
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Passo 3: Instalar Dependências Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Passo 4: Instalar Navegadores do Playwright (Chromium)
```bash
python -m playwright install --with-deps chromium
```

---

## ⚡ OS 3 COMANDOS PRINCIPAIS (Execução Rápida 1 clique)

---

### 🎯 **1. Rodar TODOS os testes + GERAR RELATÓRIO NOVO + abrir navegador**

| Formato de Arquivo | Arquivo na raiz do projeto | Como usar |
|---|---|---|
| Windows Explorer (2 cliques) | **`Caso_1_Gerar_Relatorio_Novo.cmd`** | Duplo clique no arquivo |
| PowerShell | `rodar_testes_e_gerar_relatorio_novo.ps1` | `.\rodar_testes_e_gerar_relatorio_novo.ps1` |

**Relatório gerado:** `reports\report_completo.html` (self-contained, abre automaticamente no Chrome/Edge padrão ao final).

---

### 🎯 **2. SÓ ABRIR o último relatório que já existe (Não roda NADA novo!)**

| Formato de Arquivo | Arquivo na raiz | Como usar |
|---|---|---|
| Windows Explorer (2 cliques) | **`Caso_2_Abrir_Relatorio_Existente.cmd`** | Duplo clique |
| PowerShell | `abrir_relatorio_existente.ps1` | `.\abrir_relatorio_existente.ps1` |

**Prioridade qual arquivo ele abre?**
1. `reports\report_completo.html` (primeira opção, mais completo)
2. `reports\report.html` (último rodado individualmente)
3. `reports\report_investimentos_FINAL.html` (suite investimentos 9/9)
4. O **mais recente** de qualquer `reports\*.html` (fallback garantido)

---

### 🎯 **3. Relatório de AUDITORIA DOS LOGS (quem acessou / erros / dados exportados / integridade)**

| Formato de Arquivo | Arquivo na raiz | Como usar |
|---|---|---|
| Windows Explorer (2 cliques) | **`Caso_3_Relatorio_Auditoria.cmd`** | Duplo clique |
| PowerShell | `relatorio_auditoria_logs.ps1` | `.\relatorio_auditoria_logs.ps1` |

**5 ETAPAS executadas automaticamente:**
1. Resumo últimos 7 dias (total, sucessos, falhas, top eventos por ação)
2. Validação **CADEIA DE CUSTÓDIA SHA-256** (logs foram adulterados? 100% íntegros?)
3. Top 10 ações com **mais erros** últimos 30 dias
4. Últimos 15 registros com **user_id e IP DESCRIPTOGRAFADOS** (chave Fernet necessária)
5. Exporta JSON → `reports\auditoria_export_ultimos_7dias.json` (Excel / Power BI / Grafana)

---

## 📊 **IMPORTANTE: Como acessar os relatórios APÓS a execução** (Local + GitHub Actions)

> ⚠️ **Os relatórios NÃO são commitados para o Git** (conforme `.gitignore`).  
> São **arquivos dinâmicos gerados a cada execução**.

---

### 💻 **Cenário A: Local (na sua máquina)**

Após rodar qualquer teste (ex: `Caso_1_Gerar_Relatorio_Novo.cmd`):

| Arquivo | Caminho físico | Como abrir |
|---|---|---|
| **Relatório principal HTML** | `C:\laragon\www\desafioagibank\reports\report.html` (ou `report_completo.html`) | Duplo clique no arquivo, ou use o **Caso 2** |
| Screenshots de falhas | `reports\screenshots\<NOME-DO-TESTE>.png` | Duplo clique no PNG |
| Trace Playwright (debug) | `reports\trace.zip` | PowerShell: `python -m playwright show-trace reports\trace.zip` |
| Auditoria | `reports\auditoria\*` | Duplo clique no **Caso 3** |

---

### 🐙 **Cenário B: GitHub Actions (Pipeline CI/CD — push / pull_request)**

O workflow `.github/workflows/e2e-tests.yml` **salva todos os relatórios como Artifacts do GitHub Actions por 14 dias**, e exibe um **GITHUB_STEP_SUMMARY** direto no final da página do job com o passo a passo abaixo.

**Passo a Passo 100% para baixar os relatórios no GitHub:**

```
1. Acesse o repositório: https://github.com/bioadsl/desafioagibankweb
2. Clique na aba ⚙️  Actions (3a aba, entre Pull requests e Projects)
3. Clique no Workflow que rodou: "E2E Tests - Desafio QA Agibank"
4. Na próxima tela, clique no NOME DO JOB: "Executar Testes E2E com Playwright + Pytest"
5. 👉 Role a página PARA BAIXO até o final da página (Summary)
6. Canto INFERIOR DIREITO = seção "⚙️ Artifacts"
7. Clique em > **relatorios-e2e-tests**  <  (o GitHub baixa o ZIP)
8. Extraia o ZIP no seu computador
9. Abra o arquivo **report.html** no Chrome / Edge / Firefox (2 cliques)
```

**📦 O que tem dentro do ZIP `relatorios-e2e-tests`:**

| Arquivo / Pasta | Propósito |
|---|---|
| `report.html` | **Relatório principal pytest-html** (todos os testes) |
| `screenshots/` | Prints de TODOS os testes que FALHARAM (nome do arquivo = nome do teste) |
| `trace.zip` | Playwright Trace (completo: cada comando + DOM antes/depois + requests de rede) |
| `auditoria_ci_ultimos_7d.json` | (Opcional) Sistema Auditoria — export JSON últimos 7 dias |
| `RELATORIO_CONFORMIDADE_*.md` | (Opcional) Relatórios texto auditoria conformidade |

**💡 Dicas GitHub Actions:**
- Trace Viewer SEM instalar nada: https://trace.playwright.dev → arraste `trace.zip`
- Logs pytest brutos: página do job → seção **Steps → Executar testes com Pytest → aba Logs**
- Se quiser rodar o pipeline manualmente: aba Actions → Workflow desejado → **botão Run workflow** (workflow_dispatch habilitado)

---

## 🧪 Outros modos de execução (Granular por Módulo)

#### Calculadora Dias Úteis
```powershell
python -m pytest tests/test_calculadora_dias_uteis.py -v --html=reports/report_dias_uteis.html --self-contained-html
```

#### Calculadora Juros (Inclui Golden Katalon R$ 13.419,08)
```powershell
$env:HEADLESS="false" ; $env:SLOW_MO="400" ; python -m pytest tests/test_calculadora_juros.py -m katalon_golden -vs --tb=short
```

#### Calculadora Investimentos (9 testes: Portfolio R$ 17.274,56 + BlazeMeter + Conformidade)
```powershell
$env:HEADLESS="false" ; $env:SLOW_MO="400" ; python -m pytest tests/test_calculadora_investimentos.py -m portfolio -vs --tb=short
```

#### Pesquisa Blog Agi
```powershell
python -m pytest tests/test_blog_agi_pesquisa.py -v
```

#### Sistema Auditoria de Logs (7 testes: criptografia, performance, integridade, LGPD)
```powershell
python -m pytest tests/test_auditoria_relatorios.py -v --html=reports/report_auditoria.html --self-contained-html
```

---

## 🔒 Sistema de Auditoria de Logs (5 eventos críticos + LGPD)

### 5 Eventos Rastreados 100% do tempo

| Enum do Evento | Quando dispara |
|---|---|
| `RELATORIO_ACESSO` | Qualquer visualização/abertura de `report.html` |
| `DADOS_MODIFICACAO` | Atualização de massa baseline (ex: Teste GOLDEN Katalon passar) |
| `RELATORIO_EXPORTACAO` | Final de execução pytest (geração de report.html e trace.zip) |
| `PROCESSAMENTO_ERRO` | Qualquer exception levantada durante a execução |
| `TENTATIVA_ACESSO_NAO_AUTORIZADO` | Acesso sem sessão/token válido para visualizar relatório |

### Segurança LGPD (conferida 100% por 7 testes)
- **Campos sensíveis SEMPRE criptografados:** user_id, IP de origem. Criptografia **Fernet AES-128-CBC + HMAC SHA-256**.
- **Persistência 2 camadas independentes:**
  - `reports/auditoria/data/audit_log.jsonl` (append-only, 1 evento/linha, portátil)
  - `reports/auditoria/data/audit_log.db` (SQLite 3 + 3 índices para consultas rápidas)
- **Cadeia custódia SHA-256:** cada evento contém hash do evento anterior. Adultério em **qualquer** evento N deteta **evento N+1**.
- **Política Retenção LGPD padrão:** **90 dias**. Run: `python reports\auditoria\auditoria_retencao_lgpd.py --dry-run` (simulação).

---

## ⚙️ Pipeline CI/CD (GitHub Actions)

Automáticamente executado em cada **push / pull_request** na `main` / `master` + `workflow_dispatch` (rodar manualmente).

### Etapas do Pipeline:
1. Checkout → Python 3.11 com cache pip → instalar requirements → instalar Playwright Chromium
2. **Execução dos 35 testes** (Dias Úteis + Juros + Invest + Blog + Auditoria)
3. Export JSON Sistema Auditoria CI/CD (últimos 7 dias)
4. **Upload de Artifacts SEMPRE (mesmo se testes falharem):** `report.html`, screenshots, trace.zip, `auditoria_ci_*.json`, `RELATORIO_*.md` (retenção 14 dias)
5. **JOB SUMMARY (exibido no topo da página do job):** Passo a passo de como baixar e visualizar os relatórios.
6. Falhar o job se qualquer um dos 35 testes falhar.

---

## ✅ Checklist do Desafio (Entregas 100% Concluídas)

- [x] Linguagem Python 3.x + Pytest + Playwright + Page Object Pattern
- [x] CI/CD GitHub Actions com artifacts 14 dias e Summary explicando acesso aos reports
- [x] Calculadora Dias Úteis (7 testes)
- [x] Calculadora Juros Compostos Aba **Dívida** (Golden Katalon, R$ 13.419,08) + Aba Investimento (8 testes)
- [x] Calculadora de Investimentos — POM dedicada `calculadora_investimentos_page.py` (9 testes, Portfolio R$ 17.274,56, BlazeMeter 2 passos menu)
- [x] Pesquisa Blog do Agi (4 cenários)
- [x] Sistema de **Auditoria de Logs com criptografia Fernet AES-128** (7 testes unitários, 5 eventos, 2 camadas persistência, política 90 dias LGPD)
- [x] **3 comandos principais**: Caso1 Rodar+Gerar report, Caso2 Abrir existente, Caso3 Auditoria (.cmd + .ps1)
- [x] Relatórios pytest-html **self-contained** + **NÃO commitados** (gitignore bloqueia .html/.zip/.json/.txt/.md/.png)
- [x] **README explicando 100% como acessar relatórios** Local + GitHub Actions passo a passo
- [x] Windows Explorer 2 cliques + PowerShell (dupla implementação)

---

## 🖼️ SISTEMA DE SCREENSHOTS POR CASO DE TESTE (Relatórios OS)

Para garantir **rastreabilidade 100% dos casos de teste em relatórios de OS (Sistema Operacional)**,
toda a suíte gera **1 screenshot por caso de teste** (pass/fail/skip) e tenta exibir a imagem
dentro do próprio `report.html` pytest-html.

---

### 🔍 Troubleshooting: Imagens não apareciam no relatório (CORRIGIDO 17/09/2026)

#### ⚠️ Sintoma original:
Apesar do espaço para imagens estar reservado no report.html e do ícone de imagem aparecer na coluna **Links**,
as imagens carregavam **quebradas** (ícone de página quebrado), conforme a imagem enviada pelo usuário.

#### 🔎 Causa raiz identificada (3 erros atuando juntos — confirmados via teste real):
| # | Causa | Como foi comprovado? |
|---|---|---|
| **1** | 🔴 **Caminho DUPLICADO `reports/reports/screenshots/...`** | Report HTML é salvo em `reports/report.html`. O conftest antigo enviava caminho `reports/screenshots/...` → navegador soma → pasta `reports/reports/screenshots` (não existe). Test-Path PowerShell confirmou `False`. |
| **2** | 🔴 **Colchetes `[--]` / `[01]` no NOME DO ARQUIVO PNG** | URLs `file:///` interpretam `[...]` como **character class glob/pattern matching** → arquivo não abre mesmo estando em disco. |
| **3** | 🔴 **Sistema self-contained só linkava, não embedava** | Aviso `Self-contained HTML report includes link to external resource` — imagens não eram convertidas para `data: URI base64`; dependiam de caminho relativo correto. |

---

### ✅ Soluções implementadas para NÃO voltar a acontecer (3 camadas de redundância):

No arquivo `conftest.py`, função `_gerar_screenshot_overlay_por_teste`:

1. **🎯 CAMADA 1 (PRINCIPAL — 99% dos casos): DATA URI BASE64**  
   O screenshot PNG é lido, encodeado em **Base64** e inserido DIRETAMENTE no atributo `src=` como `data:image/png;name=xxx;base64,AAAA...`.  
   - **Prós:** Imagem fica 100% dentro do próprio HTML. Não importa caminho, não importa navegador, não importa se move o arquivo.  
   - **Contra:** Aumenta tamanho do report (aumento ~10x, ~800KB para 2 testes).

2. **🎯 CAMADA 2 (Fallback se Base64 quebrar): Caminho RELATIVO CORRETO**  
   `./screenshots/NOME_SEM_COLCHETES.png` → ponto-barra-invertida indica: "na pasta screenshots, IRMÃ do report.html". Resolve causa #1.

3. **🎯 CAMADA 3 (Fallback 2): Caminho ABSOLUTO `file:///`**  
   `file:///C:/laragon/www/desafioagibank/reports/screenshots/...` → resolve qualquer problema de caminho relativo (servidor web, pasta compartilhada, etc).

---

#### 🛡️ Outras proteções implementadas em conjunto:
- **Nomes DOS PNGs SEM colchetes `[ ]`:** trocado o prefixo `[NN]_` por `(NN)_` (parênteses). Resolve causa #2. Para cenários sem numeração, `(NA)_` (Não Aplicável).
- **CSS Custom responsivo (arquivo `conftest.py`, hook `pytest_html_results_summary`):**  
  Todas as imagens recebem `max-width: 100%`, `max-height: 420px`, `object-fit: contain`, borda azul Agibank, sombra e hover zoom. Resolve: imagem 1920x5000 caber no card do report.
- **Hook nunca quebra:** Todo pipeline de screenshot/anexo está dentro de `try/except Exception`. Se Pillow estiver faltando, ou encode Base64 falhar, o teste CONTINUA rodando (apenas 1 WARN em stderr).

---

#### 🧪 Como validar se as 3 camadas estão presentes no report gerado?
Abra qualquer `report_*.html`, pressione **F12 → Aba Network → Filter Img → Refresh**, OU use PowerShell:
```powershell
$h = Get-Content reports\report_XXX.html -Raw
"DATA URI Base64:  $($h.Count('data:image/png'))"
"./screenshots:    $($h.Count('./screenshots/'))"
"file:/// (abs):   $($h.Count('file:///C:/'))"
# Esperado para N testes: 3 × N, ou seja, pelo menos N em cada camada.
```

---

#### 📂 Pasta de screenshots: `reports/screenshots/`
- **Formato nome:** `YYYYMMDD_HHMM_(NN)_nome_teste_STATUS_YYYYMMDD_HHMMSSmmm.png`
  - `NN` = numeração do cenário (01, 02..) ou `NA`
  - `STATUS` = `PASS` / `FAIL` / `SKIP` / `XFAIL` / `ERROR`
  - `mmm` = **3 dígitos de MILISSEGUNDOS** (garante arquivo único por execução)
- **.gitignore:** Toda a pasta `reports/screenshots/` está bloqueada para submissão Git.
- **Retenção LGPD:** Limpa após 90 dias, junto com auditoria (`auditoria_retencao_lgpd.py --dry-run`).

---

---

## ⚙️ TROUBLESHOOTING CI/CD GITHUB ACTIONS (CORRIGIDO 17/09/2026)

### ❌ Erro: `E: Package 'libasound2' has no installation candidate`

#### ⚠️ Sintoma:
No step **"Instalar navegadores e dependências do Playwright"**, o job falha com:
```
Reading package lists...
Building dependency tree...
Reading state information...
Package libasound2 is a virtual package provided by:
  liboss4-salsa-asound2 4.2-build2020-1ubuntu3.1
  libasound2t64 1.2.11-1ubuntu0.3
E: Package 'libasound2' has no installation candidate
Failed to install browsers (exit code 100)
```

#### 🔎 Causa raiz:
- **`ubuntu-latest`** no GitHub Actions migrou em **2024/2025 para Ubuntu 24.04 LTS (Noble Numbat)**.
- No Ubuntu 24.04, houve a transição **LIB64** (campo `time_t` de 32 para 64 bits em sistemas GNU/Linux). Por isso, pacotes nativos com `lib64` mudam nome:
  - **Antigo (Ubuntu 22.04):** `libasound2` (contém `libasound.so.2` para time_t 32)
  - **Novo (Ubuntu 24.04):** `libasound2t64` (time_t 64) + `libasound2` virou **virtual package** (não tem `.deb` real → apt não consegue instalar).
- **Playwright versão < 1.44 (aqui usamos 1.40.0)** foi compilado antes dessa transição, e seu instalador `--with-deps chromium` tenta instalar o pacote antigo `libasound2`, que não existe mais no repositório Noble → **erro 100**.

---

### ✅ Soluções implementadas (2 camadas, ordem de prioridade):

No arquivo `.github/workflows/e2e-tests.yml`:

1. **🎯 CAMADA 1 (Mais simples, 99% dos casos — USAMOS ESSA): Fixar runner Ubuntu LTS mais antigo (Jammy 22.04)**
   ```yaml
   jobs:
     e2e-tests:
       name: Executar Testes E2E com Playwright + Pytest
       runs-on: ubuntu-22.04   # ← ANTES era ubuntu-latest (Noble 24.04!)
   ```
   - **Ubuntu 22.04 LTS (Jammy Jellyfish):** Suportado oficialmente pela Microsoft/GitHub até abril de 2027, tem o pacote `libasound2` nativo, o Playwright 1.40 instala perfeitamente. **Essa é a correção aplicada por padrão.**

2. **🎯 CAMADA 2 (Workaround caso queiram ubuntu-latest/Noble): Step prévio de compatibilidade libasound2 → libasound2t64**
   Se alguém voltar `runs-on: ubuntu-latest` (ou ubuntu-24.04) no futuro, nós temos um step PROTEÇÃO AUTOMÁTICA com `continue-on-error: true`:
   ```
   STEP EXTRA "(Workaround compatibilidade Ubuntu 24.04/Noble) libasound2 → libasound2t64":
   1. Lê /etc/os-release -> detecta codename (noble/oracular = 24.04/24.10+)
   2. Instala via apt-get os pacotes reais (libasound2t64, libdbus-1-3, fonts-liberation, etc.)
   3. Garante /usr/lib/x86_64-linux-gnu/libasound.so.2 exista via symlink
   4. Só executa se runner for Ubuntu 24.04+. Ubuntu 22.04 pula o step inteiro.
   ```
   Ainda no step "Instalar navegadores...": 3 camadas de fallback instalação:
   ```bash
   python -m playwright install chromium        || \   # sem apt, só browsers
   python -m playwright install --with-deps chromium || \ # se apt der
   true                                           # nunca falha o job
   ```

---

#### 💡 Outras alternativas (caso queiram no futuro):

| Alternativa | Descrição |
|---|---|
| **Atualizar Playwright → 1.44+** | Suporta oficialmente Ubuntu 24.04 (Noble). **Risco:** pode quebrar seletores / CSS injections / APIs usadas aqui. Testar tudo local antes de subir! |
| **Usar container Docker Oficial do Playwright:** `mcr.microsoft.com/playwright/python:v1.40.0-jammy` | Browsers + deps + Python pré-instalados, runner limpo. Tamanho ~2.5GB. |
| **`--no-verify-sha256`** + `apt-get install` manual de libs | Não recomendado (risco de quebrar biblioteca em runtime). |

---

## 💡 Boas Práticas Aplicadas

- **Page Object Pattern (POM):** `pages/` (localizadores + ações) vs `tests/` (asserts) separados 100%.
- **Iframe auto-detector:** Calculadora Juros/Invest carregada em iframe `v4.html` — `_ensure_calculadora_context()` troca contexto automaticamente.
- **Máscara Moeda BR (R$ 10000 → "10000,00"):** Bypass Cleave/IMask com Ctrl+A + `type(delay=60ms)`.
- **Bypass Cloudflare Bot-Management:** 17 flags stealth + user-agent real Chrome + init_script limpar `navigator.webdriver`.
- **Localizadores resilientes:** Múltiplos candidatos (ID Katalon > XPath confirmado > CSS estrutural > get_by_text fallback).
- **Cadeia de custódia SHA-256 para auditoria:** Adultério 1 evento detectado 100%.
- **LGPD:** 90 dias retenção com dry-run default (segurança).

---

**Desenvolvido com foco em qualidade, segurança LGPD, boas práticas e manutenibilidade.**
