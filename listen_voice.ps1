
$ErrorActionPreference = "Stop"
$recognizer = $null

try {
    Add-Type -AssemblyName System.Speech

    Write-Output "CompAI: Finding English recognizer..."

    $english = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() |
        Where-Object { $_.Culture.Name -eq "en-US" } |
        Select-Object -First 1

    if ($null -eq $english) {
        throw "English recognizer not found."
    }

    $recognizer = New-Object `
        -TypeName System.Speech.Recognition.SpeechRecognitionEngine `
        -ArgumentList $english

    # Commands CompAI understands.
    $commands = @(
        "open chrome",
        "open google chrome",
        "open vscode",
        "open visual studio code",
        "open discord",
        "open calculator",
        "open notepad",
        "open explorer",
        "open file explorer",
        "open settings",
        "open steam",
        "open spotify",
        "open edge",
        "open firefox",
        "apps",
        "help",
        "status",
        "monitor",
        "pc status",
        "cpu",
        "memory",
        "ram",
        "disk",
        "battery",
        "processes",
        "top cpu",
        "top memory",
        "share",
        "share email",
        "share nearby",
        "developer mode",
        "developer mode status",
        "developer mode on",
        "developer mode off",
        "exit"
    )

    # Build a restricted speech grammar.
    $choices = New-Object System.Speech.Recognition.Choices

    foreach ($phrase in $commands) {
        [void]$choices.Add($phrase)
    }

    $builder = New-Object System.Speech.Recognition.GrammarBuilder
    $builder.Culture = $english.Culture
    $builder.Append($choices)

    $grammar = New-Object System.Speech.Recognition.Grammar($builder)

    $recognizer.LoadGrammar($grammar)

    $recognizer.InitialSilenceTimeout = [TimeSpan]::FromSeconds(8)
    $recognizer.EndSilenceTimeout = [TimeSpan]::FromSeconds(1)

    Write-Output "CompAI: Connecting to microphone..."

    $recognizer.SetInputToDefaultAudioDevice()

    Write-Output "LISTENING: Speak a CompAI command."

    $result = $recognizer.Recognize(
        [TimeSpan]::FromSeconds(12)
    )

    if ($null -eq $result) {
        Write-Output "NO_SPEECH"
    }
    else {
        Write-Output ("COMMAND:" + $result.Text)
        Write-Output ("CONFIDENCE:" + $result.Confidence)
    }
}
catch {
    Write-Output ("ERROR:" + $_.Exception.Message)
}
finally {
    if ($recognizer) {
        $recognizer.Dispose()
    }
}
