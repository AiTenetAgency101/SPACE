# AiFACTORi  Task Registry

param([string]$Intent)

switch ($Intent.ToLower()) {

    "scan" {
        @{
            Name        = "System Scan"
            Description = "Simulated scan of AiFACTORi core components."
            Steps       = @(
                "Check IdentityMemory",
                "Check Architecture",
                "Check AgentEngine"
            )
        }
    }

    "status" {
        @{
            Name        = "Status Report"
            Description = "Summarise current AiFACTORi system state."
            Steps       = @(
                "Identity present",
                "Architecture loaded",
                "AgentEngine ready"
            )
        }
    }

    default {
        @{
            Name        = "Generic Intent"
            Description = "No special mapping; generic execution."
            Steps       = @(
                "Log intent",
                "Route to AgentEngine"
            )
        }
    }
}

