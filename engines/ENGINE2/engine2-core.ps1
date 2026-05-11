# ENGINE2 CORE (TESLA / NEWTON / EINSTEIN)
param(
    [ValidateSet('newton','tesla','einstein')]
    [string]$Mode = 'newton'
)

$Engine = [ordered]@{
  id    = 'ENGINE2'
  role  = 'multi-shell'
  mode  = $Mode
  state = 'online'
}

'ENGINE2: READY'
"MODE:  $($Engine.mode)"
"STATE: $($Engine.state)"
