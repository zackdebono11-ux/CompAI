
$ErrorActionPreference = "Stop"
$recognizer = $null

try {
    Add-Type -AssemblyName System.Speech

    $english = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() |
        Where-Object { $_.Culture.Name -eq "en-US" } |
        Select-Object -First 1

    if ($null -eq $english) {
        throw "English recognizer not found."
    }

    $recognizer = New-Object `
        -TypeName System.Speech.Recognition.SpeechRecognitionEngine `
        -ArgumentList $english

    # Use unrestricted dictation for this diagnostic.
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)

    $recognizer.MaxAlternates = 5
    $recognizer.InitialSilenceTimeout = [TimeSpan]::FromSeconds(15)
    $recognizer.EndSilenceTimeout = [TimeSpan]::FromSeconds(1)

    $recognizer.SetInputToDefaultAudioDevice()

    Write-Host "CompAI: English dictation test."
    Write-Host "CompAI: Say: Open Chrome."
    Write-Host "CompAI: Speak normally, then pause."

    $result = $recognizer.Recognize(
        [TimeSpan]::FromSeconds(15)
    )

    if ($null -eq $result) {
        Write-Host "CompAI: No recognition result."
    }
    else {
        Write-Host "`n===== RECOGNITION RESULTS ====="

        foreach ($alternative in $result.Alternates) {
            Write-Host "Heard:" $alternative.Text
            Write-Host "Confidence:" $alternative.Confidence
            Write-Host "-----------------------------"
        }
    }
}
catch {
    Write-Host "CompAI test failed:" $_.Exception.Message
}
finally {
    if ($recognizer) {
        $recognizer.Dispose()
    }
}
