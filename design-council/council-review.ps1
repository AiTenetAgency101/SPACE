param(
    [string]$Module,
    [string]$Type,
    [string]$Path
)

$stamp = Get-Date -Format o

'COUNCIL-REVIEW: ACTIVE'
"MODULE: $Module"
"TYPE:   $Type"
"PATH:   $Path"
"STAMP:  $stamp"
"STATUS: PENDING-APPROVAL"
