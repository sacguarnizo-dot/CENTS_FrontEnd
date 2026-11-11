$env:KIVY_HOME = "$PSScriptRoot\.kivy"

if (Test-Path "C:\Users\I.L.M\AppData\Local\Programs\Python\Python310\python.exe") {
    & "C:\Users\I.L.M\AppData\Local\Programs\Python\Python310\python.exe" "$PSScriptRoot\principal.py"
} else {
    python "$PSScriptRoot\principal.py"
}
