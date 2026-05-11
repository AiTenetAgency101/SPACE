# AGENT CORE (NODE)
param()

$Agent = [ordered]@{
  id      = 'agent.core'
  role    = 'compute-node'
  lattice = 'SCYRONISED'
  state   = 'online'
}

'AGENT-CORE: READY'
"ID:      $($Agent.id)"
"ROLE:    $($Agent.role)"
"LATTICE: $($Agent.lattice)"
"STATE:   $($Agent.state)"
