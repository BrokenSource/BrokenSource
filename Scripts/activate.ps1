#!/usr/bin/env pwsh
Set-Location -Path (Get-Location).Parent.FullName
& ./Website/get.ps1
