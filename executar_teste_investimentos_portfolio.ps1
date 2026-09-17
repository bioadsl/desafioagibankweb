# executar_teste_investimentos_portfolio.ps1
# =============================================================================
# COMANDO EXECUTAVEL (NOVO): Teste GOLDEN da Calculadora de Investimentos
#                           (Cenario Padrao 12 meses: 10k inicial + 500/mes
#                            @ 0,80% a.m.)
# =============================================================================
# ESTRUTURA 100% COMPATIVEL com o padrao do comando de juros fornecido:
#   1) cd para a mesma pasta raiz desafioagibank
#   2) $env:HEADLESS = "false"   => mesma regra (janela Chrome VISIVEL max.)
#   3) $env:SLOW_MO  = "400"    => mesmo delay de 400ms entre acoes
#   4) pytest flags IDENTICAS:
#        -m portfolio  => executa o marker "portfolio" (CENARIO GOLDEN de
#                        investimentos com asserts exatos, analogo ao
#                        katalon_golden da aba divida em test_calculadora_juros.py)
#        -vs           => verbose + stdout no console (mesmo do exemplo)
#        --tb=short    => traceback curto (mesmo do exemplo)
# =============================================================================

Set-Location -Path "C:\laragon\www\desafioagibank"
$env:HEADLESS = "false"
$env:SLOW_MO  = "400"
python -m pytest tests/test_calculadora_investimentos.py -m portfolio -vs --tb=short
