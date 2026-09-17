# executar_teste_juros_katalon_golden.ps1
# =============================================================================
# COMANDO EXECUTAVEL: Teste GOLDEN Katalon Recorder da Calculadora de Juros
#                    (Aba Divida - Cenario 10k / 2,5% a.m. / 24 meses)
# =============================================================================
# Estrutura e padrao EXATOS conforme fornecido pelo usuario:
#   1) cd para a pasta raiz do projeto desafioagibank
#   2) $env:HEADLESS = "false"   => abre janela Chrome VISIVEL maximizada
#   3) $env:SLOW_MO  = "400"    => 400ms de delay entre acoes (visualizar passo a passo)
#   4) pytest flag:  -m katalon_golden  => executa APENAS marker katalon_golden
#                    -vs                 => verbose + print stdout no console
#                    --tb=short         => traceback curto em caso de erro
# =============================================================================

Set-Location -Path "C:\laragon\www\desafioagibank"
$env:HEADLESS = "false"
$env:SLOW_MO  = "400"
python -m pytest tests/test_calculadora_juros.py -m katalon_golden -vs --tb=short
