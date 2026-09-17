# Desafio QA Agibank - Automação de Testes Web

Framework de automação de testes E2E (End-to-End) desenvolvido como solução para o desafio técnico de QA do Agibank. Implementa validações para três funcionalidades principais: Calculadora de Dias Úteis, Calculadora de Juros Compostos e a funcionalidade de pesquisa de artigos no Blog do Agi.

---

## 🛠️ Stack Técnica

| Componente          | Tecnologia                          | Versão  |
|---------------------|-------------------------------------|---------|
| Linguagem           | Python                              | 3.11+   |
| Framework de Teste  | Pytest                              | 7.4.x   |
| Automação Web       | Playwright (Chromium)               | 1.40.x  |
| Relatórios          | pytest-html (HTML self-contained)   | 4.1.x   |
| Padrão Arquitetural | Page Object Pattern (POM)           | -       |
| CI/CD               | GitHub Actions (ubuntu-latest)      | -       |
| Cross-Platform      | Windows / Linux / macOS             | -       |

---

## 📁 Estrutura do Projeto

```
desafioagibank/
├── .github/
│   └── workflows/
│       └── e2e-tests.yml             # Pipeline CI/CD (GitHub Actions)
├── pages/                             # Camada Page Objects (POM)
│   ├── base_page.py                   # Classe base (comum a todas páginas)
│   ├── calculadora_dias_uteis_page.py # POM Calculadora Dias Úteis
│   ├── calculadora_juros_page.py      # POM Calculadora Juros Compostos
│   └── blog_agi_page.py               # POM Pesquisa de Artigos (Blog do Agi)
├── tests/                             # Camada de Casos de Teste (Pytest)
│   ├── test_calculadora_dias_uteis.py # Testes Calculadora Dias Úteis
│   ├── test_calculadora_juros.py      # Testes Calculadora Juros Compostos
│   └── test_blog_agi_pesquisa.py      # Testes Pesquisa Blog do Agi
├── reports/                           # Relatórios + screenshots (gerados pós-execução)
│   ├── report.html                    # Relatório consolidado (pytest-html)
│   ├── screenshots/                   # Screenshots em caso de falha
│   └── trace.zip                      # Playwright trace para debug
├── conftest.py                        # Fixtures Playwright + hooks Pytest
├── requirements.txt                   # Dependências do projeto
├── pytest.ini                         # Configurações do Pytest
└── README.md                          # Este arquivo
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
# Clone o repositório (substitua pelo seu link GitHub)
git clone <https://github.com/SEU-USUARIO/desafioagibank.git>
cd desafioagibank

# OU, se você já possui os arquivos localmente, apenas acesse a pasta:
cd desafioagibank
```

---

### Passo 2: Criar e Ativar Ambiente Virtual (Recomendado)

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

### Passo 4: Instalar Navegadores do Playwright (Apenas Chromium necessário)
```bash
python -m playwright install --with-deps chromium
```

> 💡 **Linux/macOS** podem precisar de `sudo` para instalar dependências do sistema (--with-deps).

---

### Passo 5: Executar os Testes

#### ▶️ Executar TODOS os testes (padrão, gera relatório em `reports/report.html`)
```bash
python -m pytest tests/ -v
```

#### ▶️ Executar apenas os testes da Calculadora de Dias Úteis
```bash
python -m pytest tests/test_calculadora_dias_uteis.py -v -m "dias_uteis"
```

#### ▶️ Executar apenas os testes da Calculadora de Juros Compostos
```bash
python -m pytest tests/test_calculadora_juros.py -v -m "juros_compostos"
```

#### ▶️ Executar apenas os testes de Pesquisa do Blog do Agi
```bash
python -m pytest tests/test_blog_agi_pesquisa.py -v -m "blog_agi"
```

#### ▶️ Executar SOMENTE cenários felizes (fluxos positivos)
```bash
python -m pytest tests/ -v -m "cenario_feliz"
```

#### ▶️ Executar SOMENTE cenários de erro / validação
```bash
python -m pytest tests/ -v -m "cenario_erro"
```

#### ▶️ Executar com navegador VISÍVEL (modo debug / headless=false)
```powershell
# Windows PowerShell
$env:HEADLESS="false"
$env:SLOW_MO="100"
python -m pytest tests/test_calculadora_dias_uteis.py::TestCalculadoraDiasUteis::test_calcular_dias_uteis_periodo_simples -v
```

```bash
# Linux/macOS
HEADLESS=false SLOW_MO=100 python -m pytest tests/ -v
```

---

## 📊 Onde encontrar os resultados?

### Relatório HTML Consolidado
```
reports/report.html
```
Abra este arquivo em qualquer navegador para visualizar os testes aprovados/falhos com detalhes.

### Screenshots (gerados automaticamente apenas em caso de falha)
```
reports/screenshots/<NOME_DO_TESTE>.png
```

### Playwright Trace (para debug avançado de falhas)
```
reports/trace.zip
```
Para inspecionar: `python -m playwright show-trace reports/trace.zip`

---

## 📝 Cobertura de Testes Implementada

### 1️⃣ Calculadora de Dias Úteis (`tests/test_calculadora_dias_uteis.py`)
| Caso de Teste                                        | Tipo         | Marcador Pytest            |
|------------------------------------------------------|--------------|----------------------------|
| Cálculo de dias úteis em período simples             | Cenário Feliz| `@cenario_feliz`           |
| Cálculo incluindo sábado e domingo                   | Cenário Feliz| `@cenario_feliz`           |
| Cálculo de semana completa (seg-sex)                 | Cenário Feliz| `@cenario_feliz`           |
| Tentativa de cálculo SEM data inicial                | Cenário Erro | `@cenario_erro`            |
| Tentativa de cálculo SEM data final                  | Cenário Erro | `@cenario_erro`            |
| Data final anterior à data inicial                   | Cenário Erro | `@cenario_erro`            |
| Validação de título e URL da página                  | Validação    | `@validacao`               |

### 2️⃣ Calculadora de Juros Compostos (`tests/test_calculadora_juros.py`)
| Caso de Teste                                        | Tipo         | Marcador Pytest            |
|------------------------------------------------------|--------------|----------------------------|
| Investimento básico (12 meses)                       | Cenário Feliz| `@cenario_feliz`           |
| Investimento de longo prazo (24 meses)               | Cenário Feliz| `@cenario_feliz`           |
| Simulação de Dívida (aba "Dívida")                   | Cenário Feliz| `@cenario_feliz`           |
| Investimento sem valor inicial (campo obrigatório)   | Cenário Erro | `@cenario_erro`            |
| Investimento sem taxa de juros (campo obrigatório)   | Cenário Erro | `@cenario_erro`            |
| Investimento sem período (campo obrigatório)         | Cenário Erro | `@cenario_erro`            |
| Validação da página carregada                        | Validação    | `@validacao`               |

### 3️⃣ Pesquisa de Artigos no Blog do Agi (`tests/test_blog_agi_pesquisa.py`)
| Caso de Teste                                        | Tipo              |
|------------------------------------------------------|-------------------|
| Cenário 1: Pesquisa de termo **relevante** ("Empréstimo") retorna resultados e valida relevância | Fluxo Principal |
| Cenário 2: Pesquisa de termo **inexistente** retorna tratamento adequado (0 resultados / mensagem) | Tratamento Borda |
| Data-driven: Pesquisa de termos financeiros comuns (FGTS, CDB, IR) | Regressão         |
| Validação do carregamento da home do blog            | Smoke Test        |

---

## ⚙️ Pipeline CI/CD (GitHub Actions)

O arquivo `.github/workflows/e2e-tests.yml` automatiza a execução de **todos os testes** em **cada push ou pull_request** nas branches `main` / `master`.

### Etapas do Pipeline:
1. **Checkout** do código-fonte
2. **Setup Python 3.11** (com cache do pip para performance)
3. **Instalação** de dependências (`requirements.txt`)
4. **Instalação** do Chromium + deps do Playwright
5. **Execução dos testes** com Pytest (headless)
6. **Upload de artefatos** SEMPRE (mesmo em falha):
   - `reports/report.html`
   - Screenshots de erros
   - Playwright trace (`trace.zip`)
7. Artefatos são **retidos por 14 dias**

> 💡 Para executar manualmente o pipeline, use o botão **Run workflow** no GitHub Actions.

---

## 💡 Boas Práticas Aplicadas no Framework

- **Page Object Pattern (POM):** Separação 100% clara entre localizadores/ações (camada `pages/`) e lógica de teste (camada `tests/`).
- **Localizadores resilientes:** Múltiplas estratégias de seletores CSS (fallback) para reduzir fragilidade em atualizações de layout.
- **Waits explícitos:** Todos os elementos aguardam `state="visible"` antes de interações — evitando flaky tests.
- **Fixtures reutilizáveis:** `conftest.py` gerencia ciclo de vida do browser/context/page (scope function).
- **Tracing + Screenshots:** Em caso de falha, provas visuais + trace completo para depuração rápida.
- **Marcadores Pytest:** Execução granular por funcionalidade/tipo de cenário.
- **Cross-platform:** Mesmo código roda em Windows, Linux e macOS (incluindo CI do GitHub).

---

## 🐛 Dicas de Debug

1. **Teste flaky?** Aumente `SLOW_MO=200` e use `HEADLESS=false` para visualizar o passo a passo.
2. **Playwright Trace Viewer:** Abra `reports/trace.zip` para ver cada comando, screenshot e snapshot DOM.
3. **Executar apenas 1 teste específico:**
   ```bash
   python -m pytest tests/test_blog_agi_pesquisa.py::TestBlogAgiPesquisa::test_pesquisa_termo_relevante_retorna_resultados -v
   ```

---

## ✅ Resumo do Desafio

- [x] Linguagem Python 3.x
- [x] Framework de Testes: Pytest
- [x] Automação Web: Playwright (Chromium, mais rápido/estável)
- [x] Padrão Page Object Pattern (POM)
- [x] CI/CD: GitHub Actions (push + pull_request, com artefatos em falha)
- [x] Estrutura de pastas exatamente como solicitada
- [x] Calculadora de Dias Úteis (cenário feliz + cenários de erro)
- [x] Calculadora de Juros Compostos (Abas "Dívida" e "Investimento")
- [x] Pesquisa Blog do Agi (lupa superior direita) — 2 cenários relevantes
- [x] Relatórios pytest-html
- [x] README.md completo com instruções de configuração/execução

---

**Desenvolvido com ❤️ foco em qualidade, boas práticas e manutenibilidade.**
