# Deploy index_v2.html to index.html using .NET IO APIs
$ErrorActionPreference = "Stop"

$v1Src = "D:\projects\Biblia-czytanie\index.html"
$v1Backup = "D:\projects\Biblia-czytanie\index_old_v1.html"
$v2Src = "D:\projects\Biblia-czytanie\index_v2.html"
$outHarm = "D:\projects\Biblia-czytanie\output\harmonogram_chrystadelfianie_2026.html"

[System.IO.File]::Copy($v1Src, $v1Backup, $true)
[System.IO.File]::Copy($v2Src, $v1Src, $true)
[System.IO.File]::Copy($v2Src, $outHarm, $true)

Write-Host "SUKCES! index.html zostal pomyslnie zaktualizowany do wersji v2 (stara wersja zachowana w index_old_v1.html)."
