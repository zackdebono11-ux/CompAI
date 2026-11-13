
$ErrorActionPreference = "Stop"

$audioPath = Join-Path $PSScriptRoot "startup.wav"
$player = $null

try {
    if (-not (Test-Path $audioPath)) {
        Write-Host "CompAI: startup.wav was not found!"
        exit 1
    }

   

    $player = New-Object System.Media.SoundPlayer
    $player.SoundLocation = $audioPath

    $player.Load()

    

    # Play the WAV and wait until it finishes.
    $player.PlaySync()

    Write-Host "CompAI: Startup sound completed!"
}
catch {
    Write-Host "CompAI: Audio playback failed:"
    Write-Host $_.Exception.Message
}
finally {
    if ($player) {
        $player.Dispose()
    }
}
