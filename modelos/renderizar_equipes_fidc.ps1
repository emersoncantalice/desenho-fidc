param()
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'renderizar_backlog_fidc.ps1') -OnlyHelpers
$data = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'cronogramas-equipes-fidc.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$colors = @{ 'Arquiteto'='#7152A3'; 'Backend'='#0033CC'; 'Frontend'='#098477'; 'QA'='#B76C00'; 'ITLead'='#606772' }
foreach ($group in $data.groups) {
    $maxFinish = ($group.plans | Measure-Object -Property finish -Maximum).Maximum
    $weeks=[int][Math]::Ceiling($maxFinish/5)
    $left=1620; $weekW=60; $rowH=65; $top=445; $w=$left+$weeks*$weekW+65
    foreach ($scenario in $group.plans) {
        $h=$top+($scenario.items.Count+1)*$rowH+135
        $bitmap,$g=Canvas $w $h
        Box $g 0 0 $w 250 $navy
        Text $g "CRONOGRAMA / $($group.name.ToUpper())" 55 24 44 '#FFFFFF' $true
        Text $g "$($scenario.developers) DESENVOLVEDORES: $($scenario.backend) Backend + 1 Frontend" 55 87 32 '#FFFFFF' $true
        Text $g "Apoio: 1 Arquiteto + 1 ITLead (20%) + 1 QA | $($scenario.people) pessoas envolvidas" 55 138 27 '#D5E0FF'
        Text $g "Prazo: $($scenario.finish) dias úteis / $($scenario.milestone) | Entregas: $($scenario.delivery_effort) du + gestão: $($scenario.lead_effort) du equivalentes" 55 190 27 '#FFFFFF'
        $x=55
        foreach ($role in @('Arquiteto','Backend','Frontend','QA','ITLead')) {
            Box $g $x 280 22 22 $colors[$role]; Text $g $role ($x+32) 275 24 $ink; $x+=230
        }
        $note=if ($group.prefix -eq 'D3') {'Base FIDC pronta é pré-requisito. Cada equipe é uma alternativa; não são equipes simultâneas.'} else {'Cada profissional executa uma atividade por vez. Backend e Frontend têm agendas separadas.'}
        Text $g $note 55 325 24 $muted
        Text $g 'ID / ATIVIDADE' 55 402 23 $muted $true
        Text $g 'PERFIL / PESSOA' 1190 402 23 $muted $true
        Text $g 'DU INÍCIO–FIM' 1430 402 21 $muted $true
        for ($i=0;$i -lt $weeks;$i++) {
            $x=$left+$i*$weekW
            if ($i%4 -eq 0) { Text $g "M$([int][Math]::Floor($i/4)+1)" $x 370 23 $blue $true }
            Text $g "S$($i%4+1)" ($x+8) 407 19 $muted
        }
        $y=$top; $index=0
        foreach ($item in $scenario.items) {
            if ($index%2 -eq 0) { Box $g 45 $y ($w-90) $rowH '#F3F5FA' }
            Text $g $item.id 55 ($y+19) 24 $navy $true
            $lines=Wrap $g $item.title 23 930
            if ($lines.Count -gt 2) { throw "Título excede duas linhas: $($item.id)" }
            $ty=if ($lines.Count -gt 1) {$y+3} else {$y+19}
            foreach ($line in $lines) { Text $g $line 220 $ty 23 $ink; $ty+=29 }
            Text $g $item.resource 1190 ($y+19) 24 $colors[$item.role] $true
            Text $g "$($item.start)–$($item.end)" 1430 ($y+19) 24 $muted
            for ($i=0;$i -le $weeks;$i++) { Box $g ($left+$i*$weekW) $y 1 $rowH '#D7DEEB' }
            Box $g ($left+($item.start-1)*$weekW/5) ($y+19) ($item.duration*$weekW/5) 27 $colors[$item.role]
            $y+=$rowH; $index++
        }
        Box $g 45 $y ($w-90) $rowH '#EDF0F5'
        Text $g 'GESTÃO' 55 ($y+19) 24 $navy $true
        Text $g 'Planejamento, riscos, dependências e entregas (20% de dedicação)' 220 ($y+19) 23 $ink
        Text $g 'ITLead 1' 1190 ($y+19) 24 $colors['ITLead'] $true
        Text $g "1–$($scenario.finish)" 1430 ($y+19) 24 $muted
        Box $g $left ($y+19) ($scenario.finish*$weekW/5) 27 $colors['ITLead']
        $y+=$rowH
        Text $g 'Semana = 5 dias úteis | Mês = 20 dias úteis | Barras por profissional; gestão com dedicação parcial.' 55 ($y+25) 23 $muted
        Text $g 'B / F / Q no ID: divisão da atividade original entre Backend, Frontend e QA, preservando o esforço total.' 55 ($y+62) 23 $muted
        Save $bitmap $g "cronograma-$($group.slug)-$($scenario.developers)-devs"
    }
    # Mesmo eixo de tempo para comparar as três alternativas de capacidade.
    $left=950; $w=$left+$weeks*$weekW+80; $top=340; $rowH=310
    $bitmap,$g=Canvas $w 1430
    Box $g 0 0 $w 230 $navy
    Text $g "EQUIPES / $($group.name.ToUpper())" 55 30 43 '#FFFFFF' $true
    Text $g '2, 3 e 4 desenvolvedores — comparação no mesmo eixo de tempo' 55 100 28 '#FFFFFF'
    Text $g 'Arquiteto, ITLead e QA adicionais. Estimativas por capacidade e dependências.' 55 158 24 '#D5E0FF'
    for ($i=0;$i -lt $weeks;$i++) {
        $x=$left+$i*$weekW
        if ($i%4 -eq 0) { Text $g "M$([int][Math]::Floor($i/4)+1)" $x 260 22 $blue $true }
        Text $g "S$($i%4+1)" ($x+8) 300 18 $muted
    }
    $y=$top
    foreach ($scenario in $group.plans) {
        Box $g 45 $y ($w-90) ($rowH-20) '#F3F5FA'
        Text $g "$($scenario.developers) DESENVOLVEDORES" 60 ($y+20) 34 $navy $true
        Text $g "$($scenario.backend) Backend + 1 Frontend" 60 ($y+75) 28 $blue
        Text $g '1 Arquiteto: desenho da solução' 60 ($y+122) 24 $colors['Arquiteto']
        Text $g '1 ITLead: gestão (20%)' 60 ($y+159) 24 $colors['ITLead']
        Text $g '1 QA: testes e homologação' 60 ($y+196) 24 $colors['QA']
        Text $g "$($scenario.people) pessoas | $($scenario.finish) dias úteis de prazo" 60 ($y+240) 25 $navy $true
        for ($i=0;$i -le $weeks;$i++) { Box $g ($left+$i*$weekW) $y 1 ($rowH-20) '#D7DEEB' }
        Box $g $left ($y+75) ($scenario.finish*$weekW/5) 45 $blue
        Text $g "Implantação: $($scenario.milestone) / du $($scenario.finish)" ($left+10) ($y+142) 25 $navy $true
        Text $g "$($scenario.delivery_effort) du de entregas + $($scenario.lead_effort) du de gestão" ($left+10) ($y+187) 23 $muted
        $y+=$rowH
    }
    Text $g 'Cada linha é uma alternativa. Atividades e responsáveis estão nos Gantts detalhados de cada equipe.' 55 ($y+10) 22 $muted
    $note=if ($group.prefix -eq 'D3') {'A extensão documental começa com a base FIDC disponível.'} else {'Prazo recalculado por pessoa e perfil; substitui a comparação anterior por frentes.'}
    Text $g $note 55 ($y+48) 22 $muted
    Save $bitmap $g "cronograma-$($group.slug)"
}
$bitmap,$g=Canvas 2100 1160
Box $g 0 0 2100 215 $navy
Text $g 'COMPARATIVO / PERFIS E PRAZOS' 60 35 46 '#FFFFFF' $true
Text $g 'Mesa FIDC e pendência documental • 2, 3 e 4 desenvolvedores' 60 110 30 '#FFFFFF'
Text $g 'Apoio em todas as opções: 1 Arquiteto + 1 ITLead (20%) + 1 QA.' 60 250 30 $navy $true
$xs=@(60,420,1000,1370,1710)
$headers=@('Equipe','Composição dev','Pessoas','Base FIDC','Documentos')
for ($i=0;$i -lt 5;$i++) { Text $g $headers[$i] $xs[$i] 340 28 $muted $true }
$y=410
for ($i=0;$i -lt 3;$i++) {
    $a=$data.groups[0].plans[$i]; $b=$data.groups[1].plans[$i]
    Box $g 40 $y 2020 145 '#EDF2FF'
    Text $g "$($a.developers) devs" 60 ($y+44) 40 $blue $true
    Text $g "$($a.backend) Backend + 1 Frontend" 420 ($y+48) 30 $ink
    Text $g "$($a.people) pessoas" 1000 ($y+48) 30 $ink
    Text $g "$($a.finish) du" 1370 ($y+42) 40 $navy $true
    Text $g "$($b.finish) du" 1710 ($y+42) 40 $navy $true
    $y+=165
}
Text $g 'Arquiteto e QA atuam nas janelas planejadas; o ITLead acompanha o cenário com dedicação parcial.' 60 950 25 $muted
Text $g 'Documentos é uma extensão: base FIDC pronta é pré-requisito. Os prazos têm início próprio.' 60 997 25 $muted
Text $g 'du = dias úteis | Estimativas preliminares. Mais pessoas não eliminam dependências entre atividades.' 60 1044 25 $muted
Save $bitmap $g 'comparativo-equipes-fidc'
