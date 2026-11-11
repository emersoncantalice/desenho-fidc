param([switch]$OnlyHelpers)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$plan = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'backlog-fidc-documentos.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$navy = '#001E62'; $blue = '#0033CC'; $ink = '#16181C'; $muted = '#606772'; $pale = '#EDF2FF'
function Brush([string]$hex) { [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml($hex)) }
function Font([int]$size, [bool]$bold = $false) {
    $style = if ($bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
    [System.Drawing.Font]::new('Segoe UI', $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
}
function Text($g, [string]$text, [int]$x, [int]$y, [int]$size, [string]$color, [bool]$bold = $false) {
    $b = Brush $color; $f = Font $size $bold
    $g.DrawString($text, $f, $b, [single]$x, [single]$y)
    $b.Dispose(); $f.Dispose()
}
function Box($g, [int]$x, [int]$y, [int]$w, [int]$h, [string]$color) {
    $b = Brush $color; $g.FillRectangle($b,$x,$y,$w,$h); $b.Dispose()
}
function Wrap($g, [string]$value, [int]$size, [int]$width) {
    $f = Font $size; $lines = [System.Collections.Generic.List[string]]::new(); $line = ''
    foreach ($word in ($value -split '\s+')) {
        $candidate = if ($line) { "$line $word" } else { $word }
        if ($line -and $g.MeasureString($candidate,$f).Width -gt $width) { $lines.Add($line); $line = $word } else { $line = $candidate }
    }
    if ($line) { $lines.Add($line) }; $f.Dispose(); return ,$lines.ToArray()
}
function Canvas([int]$w,[int]$h) {
    $bitmap = [System.Drawing.Bitmap]::new($w,$h)
    $g = [System.Drawing.Graphics]::FromImage($bitmap)
    $g.Clear([System.Drawing.Color]::White)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    return @($bitmap,$g)
}
function Save($bitmap,$g,[string]$name) {
    $path = Join-Path $root "diagramas/$name.png"
    $bitmap.Save($path,[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bitmap.Dispose(); Write-Output $path
}
if ($OnlyHelpers) { return }
foreach ($group in $plan.groups) {
    $items = @($plan.items | Where-Object { $_.id.StartsWith($group.prefix) })
    $scratch,$sg = Canvas 2100 100
    $cards = @(); $total = 0
    foreach ($item in $items) {
        $lines = Wrap $sg $item.title 26 1470
        $depLines = Wrap $sg ('Depende de: ' + (($item.deps -join ', ') -replace '^$','nenhuma')) 21 1470
        $h = [Math]::Max(122, 62 + $lines.Count * 34 + $depLines.Count * 27)
        $cards += @{ item=$item; lines=$lines; deps=$depLines; h=$h }; $total += $h
    }
    $sg.Dispose(); $scratch.Dispose()
    $bitmap,$g = Canvas 2100 ($total + 400)
    Box $g 0 0 2100 220 $navy
    Text $g 'BACKLOG / MESA FIDC' 64 28 46 '#FFFFFF' $true
    Text $g $group.name 64 92 34 '#FFFFFF'
    Text $g "$($items.Count) itens | $($group.effort) dias úteis de esforço | Calendário próprio do cenário | 11/11/2026" 64 155 25 '#D5E0FF'
    Text $g 'ID / TIPO' 64 248 22 $muted $true
    Text $g 'ENTREGA E DEPENDÊNCIAS' 350 248 22 $muted $true
    Text $g 'FRENTE / PERÍODO' 1840 248 20 $muted $true
    $y = 295; $index=0
    foreach ($card in $cards) {
        $item = $card.item
        if ($index % 2 -eq 0) { Box $g 45 $y 2010 $card.h '#F3F5FA' }
        Text $g $item.id 64 ($y+16) 30 $blue $true
        Text $g $item.type 64 ($y+58) 23 $muted
        Text $g $item.size 64 ($y+91) 21 $muted
        $ty = $y+15
        foreach ($line in $card.lines) { Text $g $line 350 $ty 26 $ink; $ty+=34 }
        $ty+=10
        foreach ($line in $card.deps) { Text $g $line 350 $ty 21 $muted; $ty+=27 }
        Text $g $item.team 1840 ($y+16) 25 $navy $true
        Text $g "du $($item.start)–$($item.end)" 1840 ($y+57) 22 $muted
        Text $g "$($item.duration) dias úteis" 1840 ($y+90) 21 $muted
        $y += $card.h; $index++
    }
    Text $g 'Esforço não é prazo. Datas relativas ao início do projeto. Dependências e capacidade condicionam o calendário.' 64 ($y+30) 23 $muted
    Text $g 'Fonte: docs/cronograma-fidc-documentos.md | Base FIDC sem proposta interna; pendência vinculada ao protocolo.' 64 ($y+66) 21 $muted
    $name = if ($group.prefix -eq 'F3') { 'backlog-fidc' } else { 'backlog-fidc-documentos' }
    Save $bitmap $g $name
}
foreach ($timelineGroup in $plan.groups) {
$timelineItems = @($plan.items | Where-Object {$_.id.StartsWith($timelineGroup.prefix)})
$timelineFinish = $timelineGroup.finish
$timelineMonth = [int][Math]::Floor(($timelineFinish-1)/20)+1
$timelineWeek = [int][Math]::Floor((($timelineFinish-1)%20)/5)+1
$weeks = [int][Math]::Ceiling($timelineFinish / 5)
$rowH=51; $top=405; $left=1150; $weekW=60; $w=$left+$weeks*$weekW+65; $h=$top+($timelineItems.Count+1)*$rowH+130
$bitmap,$g = Canvas $w $h
Box $g 0 0 $w 230 $navy
Text $g "CRONOGRAMA / $($timelineGroup.name.ToUpper())" 55 30 44 '#FFFFFF' $true
Text $g "$($timelineItems.Count) atividades | $($timelineGroup.effort) du de esforço | 4 frentes | Implantação: M$timelineMonth·S$timelineWeek / du $timelineFinish" 55 100 29 '#FFFFFF'
Text $g "Eixo de tempo próprio: dia útil 1 ao $timelineFinish | Barras mostram início e fim de cada atividade" 55 160 26 '#D5E0FF'
Text $g 'Uma atividade por frente por vez. Cada semana = 5 dias úteis. Cada mês = 20 dias úteis.' 55 253 25 $muted
$note = if ($timelineGroup.prefix -eq 'F3') { 'Cenário base: entrada → protocolo → PDEC → mesa FIDC → resultado ao parceiro.' } else { 'Extensão: pressupõe a base FIDC disponível. Pendência → cliente → bucket → validação → reanálise.' }
Text $g $note 55 294 23 $navy
Text $g 'ID / ENTREGA' 55 363 22 $muted $true
Text $g 'FRENTE / DU' 945 363 21 $muted $true
for ($i=0; $i -lt $weeks; $i++) {
    $x=$left+$i*$weekW
    if ($i%4 -eq 0) { Text $g "M$([int][Math]::Floor($i/4)+1)" $x 335 23 $blue $true }
    Text $g "S$($i%4+1)" ($x+10) 371 19 $muted
}
$short = @{
'F3-01'='Runtime, região e MySQL'; 'F3-02'='Contratos da API e eventos'; 'F3-03'='Certificados e mTLS'; 'F3-04'='Extensões da PCRE-JULG'; 'F3-05'='Política de falhas do callback'; 'F3-06'='Arquitetura da base FIDC'; 'F3-07'='Ambientes GCP e CI/CD'; 'F3-08'='Provisionar MySQL'; 'F3-09'='Provisionar Kafka'; 'F3-10'='Provisionar mTLS'; 'F3-11'='Observabilidade'; 'F3-12'='Carga e resiliência'; 'F3-13'='Ponta a ponta da base'; 'F3-14'='Runbook e onboarding'; 'F3-15'='Homologar base para integração'; 'F3-16'='Receber solicitação FIDC'; 'F3-17'='Persistir e devolver protocolo'; 'F3-18'='Controlar estados da análise'; 'F3-19'='Decisão automática na PDEC'; 'F3-20'='Derivação no Kafka com outbox'; 'F3-21'='Idempotência da solicitação'; 'F3-22'='Fila única FIDC na mesa'; 'F3-23'='Dados e resultado na mesa'; 'F3-24'='Decisão manual por evento'; 'F3-25'='Perfis de acesso do analista'; 'F3-26'='Consolidar decisão manual'; 'F3-27'='Proteger decisão finalizada'; 'F3-28'='Callback mTLS ao parceiro'; 'F3-29'='Reprocessar falhas do callback'; 'F3-30'='Auditoria da solicitação';
'D3-01'='Regras de pendência documental'; 'D3-02'='Regras de bucket e validação'; 'D3-03'='Contratos e correlação'; 'D3-04'='Arquitetura da extensão'; 'D3-05'='Bucket privado e quarentena'; 'D3-06'='Mesa pendencia a solicitação'; 'D3-07'='Notificar parceiro e cliente'; 'D3-08'='Autorizar URL temporária'; 'D3-09'='Cliente envia ao bucket'; 'D3-10'='Validar e isolar arquivos'; 'D3-11'='Consolidar documentação'; 'D3-12'='Retomar análise uma única vez'; 'D3-13'='Consultar documentos na mesa'; 'D3-14'='Corrigir e reenviar documentos'; 'D3-15'='Homologar fluxo documental'; 'D3-16'='Go-live integrado e operação'
}
$short['F3-15']='Homologação e go-live da base'
$short['D3-16']='Go-live documental e operação'
$y=$top
foreach ($group in @($timelineGroup)) {
    Box $g 45 $y ($w-90) $rowH $pale
    Text $g "$($group.name.ToUpper()) / $($group.effort) DIAS ÚTEIS DE ESFORÇO" 55 ($y+8) 25 $blue $true
    $y+=$rowH; $idx=0
    foreach ($item in @($plan.items | Where-Object {$_.id.StartsWith($group.prefix)})) {
        if ($idx%2 -eq 0) { Box $g 45 $y ($w-90) $rowH '#F8F9FC' }
        Text $g "$($item.id)   $($short[$item.id])" 55 ($y+10) 25 $ink
        Text $g "$($item.team)  $($item.start)–$($item.end)" 945 ($y+12) 21 $muted
        for ($i=0;$i -le $weeks;$i++) { Box $g ($left+$i*$weekW) $y 1 $rowH '#D7DEEB' }
        $bx=$left+($item.start-1)*$weekW/5; $bw=$item.duration*$weekW/5
        $color = if ($group.prefix -eq 'F3') {$navy} else {$blue}
        Box $g $bx ($y+13) $bw 25 $color
        $y+=$rowH; $idx++
    }
}
Text $g 'Barras na escala de dias úteis. A coluna DU informa início–fim. Atividades completas no documento.' 55 ($y+25) 23 $muted
Text $g 'Cada cenário tem seu próprio dia 1. Não se presume execução simultânea com as mesmas equipes.' 55 ($y+62) 23 $muted
$timelineName = if ($timelineGroup.prefix -eq 'F3') { 'cronograma-fidc' } else { 'cronograma-pendencia-documental' }
Save $bitmap $g $timelineName
}
