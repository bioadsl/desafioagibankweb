param(
    [switch]$Force = $false,
    [ValidateRange(1, 3650)][int]$RetencaoDias = 90
)
$ErrorActionPreference = "Stop"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPORTS = Join-Path $ROOT "reports"
$AUDIT_DIR = Join-Path $REPORTS "auditoria"
$SCREENSHOTS_DIR = Join-Path $REPORTS "screenshots"
$AUDIT_DATA = Join-Path $AUDIT_DIR "data"
$AUDIT_KEYS = Join-Path $AUDIT_DATA "keys"
$AUDIT_EXPORTS = Join-Path $AUDIT_DIR "relatorios_extraidos"

$protect = @(
    ".gitkeep","README.md","__init__.py",
    "auditor_logger.py","auditoria_consultar.py","auditoria_retencao_lgpd.py",
    "_resumo_auditoria_executar.py","screenshot_utils.py","_tmp_valida_report.py"
)

$sep = "=" * 84
Write-Host
Write-Host $sep -ForegroundColor DarkCyan
Write-Host ("{0,74} - CLEANUP RELATORIOS AGIBANK" -f "[*]") -ForegroundColor Cyan
Write-Host $sep -ForegroundColor DarkCyan
Write-Host (" ROOT:          {0}" -f $ROOT)
Write-Host (" Reports:       {0}" -f $REPORTS)
$mode, $color = ("DRY-RUN (simulacao, NAO APAGA)", "Yellow")
if ($Force) { $mode, $color = ("EXECUCAO REAL (VAZ APAGAR)", "Red") }
Write-Host (" Modo:          ") -NoNewline
Write-Host $mode -ForegroundColor $color
Write-Host (" Retencao LGPD: $RetencaoDias dias")
Write-Host $sep -ForegroundColor DarkCyan
Write-Host


if (-not (Test-Path -LiteralPath $REPORTS)) {
    Write-Host "[INFO] Pasta reports/ nao existe - nada a fazer." -ForegroundColor Green
    exit 0
}

function fmt-size {
    param([long]$bytes)
    if ($bytes -ge 1GB) { return ("{0:N2} GB" -f ($bytes / 1GB)) }
    if ($bytes -ge 1MB) { return ("{0:N2} MB" -f ($bytes / 1MB)) }
    if ($bytes -ge 1KB) { return ("{0:N2} KB" -f ($bytes / 1KB)) }
    return "$bytes B"
}

function is-protected {
    param([string]$Path)
    $name = [IO.Path]::GetFileName($Path)
    if ([string]::IsNullOrEmpty($name)) { return $false }
    if ($protect -contains $name) { return $true }
    try {
        foreach ($k in Get-ChildItem -LiteralPath $AUDIT_KEYS -Filter "*.key" -File -ErrorAction SilentlyContinue) {
            if ([IO.Path]::GetFullPath($k.FullName) -ieq [IO.Path]::GetFullPath($Path)) { return $true }
        }
    } catch {}
    return $false
}

function scan-files {
    param([string]$Dir,[string[]]$Patterns,[int]$MaxAgeDays=0)
    $list = New-Object System.Collections.ArrayList
    if (-not (Test-Path -LiteralPath $Dir)) { return (,$list) }
    $limit = (Get-Date).AddDays(-$MaxAgeDays)
    foreach ($pat in $Patterns) {
        try { $items = Get-ChildItem -LiteralPath $Dir -Filter $pat -File -ErrorAction SilentlyContinue }
        catch { continue }
        foreach ($f in $items) {
            if (is-protected $f.FullName) { continue }
            if ($MaxAgeDays -gt 0 -and $f.LastWriteTime -gt $limit) { continue }
            [void]$list.Add($f)
        }
    }
    return (,$list)
}

$cats = @(
    @{ D="Reports (HTML/ZIP/JSON/TXT/LOG)"; P=$REPORTS; M=@("*.html","*.zip","*.json","*.txt","*.md","*.log","*.out"); R=0 },
    @{ D="Screenshots PNG/JPG";             P=$SCREENSHOTS_DIR; M=@("*.png","*.jpg","*.jpeg","*.webp","*.bmp"); R=0 },
    @{ D="Auditoria data (LGPD)";           P=$AUDIT_DATA; M=@("*.jsonl","*.db","*.sqlite3","*.sqlite","*.csv"); R=$RetencaoDias },
    @{ D="Auditoria exports";               P=$AUDIT_EXPORTS; M=@("*.json","*.csv","*.xlsx","*.html","*.txt","*.md","*.zip"); R=0 },
    @{ D="Auditoria __pycache__";           P=(Join-Path $AUDIT_DIR "__pycache__"); M=@("*.pyc","*.pyo"); R=0 }
)

$total_size = [long]0
$total_cnt  = 0
$per_cat = @{}

Write-Host " - Analisando categorias..." -ForegroundColor Cyan
foreach ($c in $cats) {
    Write-Host ("  > {0}" -f $c.D) -ForegroundColor DarkCyan
    $l = scan-files -Dir $c.P -Patterns $c.M -MaxAgeDays $c.R
    $per_cat[$c.D] = $l
    $s = [long]0; foreach ($f in $l) { $s += $f.Length }
    $col = if ($l.Count -eq 0) { "Gray" } else { "Yellow" }
    Write-Host ("    {0} arqs | {1}" -f $l.Count, (fmt-size $s)) -ForegroundColor $col
    $total_cnt += $l.Count; $total_size += $s
}

$empty_dirs = New-Object System.Collections.ArrayList
if ($Force) {
    foreach ($d in @($SCREENSHOTS_DIR, $AUDIT_EXPORTS, (Join-Path $AUDIT_DIR "__pycache__"))) {
        if (-not (Test-Path -LiteralPath $d)) { continue }
        try {
            $content = Get-ChildItem -LiteralPath $d -Force -ErrorAction SilentlyContinue
            if (-not $content -or $content.Count -eq 0) {
                $gk = Join-Path $d ".gitkeep"
                if (-not (is-protected $gk)) { [void]$empty_dirs.Add($d) }
            }
        } catch {}
    }
}

Write-Host $sep -ForegroundColor DarkYellow
Write-Host (" {0,74}" -f "[RESUMO]") -ForegroundColor Yellow
Write-Host $sep -ForegroundColor DarkYellow
Write-Host ("  Arquivos marcados: {0}" -f $total_cnt) -ForegroundColor Yellow
Write-Host ("  Espaco liberar:   {0}" -f (fmt-size $total_size)) -ForegroundColor Yellow
Write-Host ("  Pastas vazias:    {0}" -f $empty_dirs.Count) -ForegroundColor Yellow
Write-Host $sep -ForegroundColor DarkYellow
Write-Host

$ans = "S"
if ($Force) {
    if ($total_cnt -eq 0 -and $empty_dirs.Count -eq 0) {
        $ans = "N"
        Write-Host "[INFO] Nada a limpar." -ForegroundColor Green
    } elseif ($PSBoundParameters.ContainsKey('Confirm') -and -not $PSBoundParameters.Confirm) {
        $ans = "S"
    } else {
        $r = Read-Host " CONFIRMA apagar $total_cnt arqs? (S/N)  [Padrao=N]"
        if ([string]::IsNullOrWhiteSpace($r)) { $r = "N" }
        $ans = $r.ToUpperInvariant()
    }
} else {
    Write-Host "[INFO] Modo DRY-RUN (use -Force p/ apagar). Nada alterado." -ForegroundColor Green
    exit 0
}

if ($Force -and ($ans -eq "S" -or $ans -eq "SIM")) {
    $q = 0; $sz = [long]0
    Write-Host " Removendo arquivos..." -ForegroundColor Red
    foreach ($c in $cats) {
        foreach ($f in $per_cat[$c.D]) {
            try {
                if (is-protected $f.FullName) { continue }
                Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
                $q++; $sz += $f.Length
            } catch {
                Write-Host ("    [ERRO] {0} -> {1}" -f $f.Name, $_.Exception.Message) -ForegroundColor Red
            }
        }
    }
    $removed_dirs = 0
    foreach ($d in $empty_dirs) {
        try {
            if (Test-Path -LiteralPath $d) {
                Remove-Item -LiteralPath $d -Force -Recurse -ErrorAction Stop
                $removed_dirs++
            }
        } catch {}
    }
    Write-Host $sep -ForegroundColor Green
    Write-Host (" {0,74}" -f "[CONCLUIDO]") -ForegroundColor Green
    Write-Host $sep -ForegroundColor Green
    Write-Host ("  Arqs removidos:   {0}" -f $q) -ForegroundColor Green
    Write-Host ("  Espaco liberado:  {0}" -f (fmt-size $sz)) -ForegroundColor Green
    Write-Host ("  Pastas limpas:    {0}" -f $removed_dirs) -ForegroundColor Green
    Write-Host ("  Retencao LGPD:    {0} dias" -f $RetencaoDias) -ForegroundColor Green
    Write-Host $sep -ForegroundColor Green
} else {
    Write-Host " [CANCELADO] Nada foi apagado." -ForegroundColor DarkYellow
}
Write-Host
exit 0
