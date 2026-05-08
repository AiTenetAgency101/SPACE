"""
Engine Health Dashboard API
FastAPI server for health monitoring visualization and control.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import logging
from datetime import datetime
from engine_health_monitor import EngineHealthMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Engine Health Dashboard",
    description="Real-time monitoring of all 3 engines + 14-engine network",
    version="1.0.0",
)

# Global health monitor
monitor = EngineHealthMonitor()
monitor_task = None


@app.on_event("startup")
async def startup():
    """Start health monitoring loop on startup."""
    global monitor_task
    logger.info("Engine Health Dashboard starting")
    
    async def monitoring_loop():
        """Run health checks every 5 minutes."""
        while True:
            try:
                await monitor.health_check_cycle()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)
    
    monitor_task = asyncio.create_task(monitoring_loop())


@app.on_event("shutdown")
async def shutdown():
    """Cancel monitoring task on shutdown."""
    if monitor_task:
        monitor_task.cancel()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Engine Health Dashboard",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/engines/status")
async def get_engines_status():
    """Get current status of all engines."""
    status = monitor.get_current_status()
    return {
        "status": "success",
        "timestamp": status["timestamp"],
        "engines": status["engines"],
        "active_alerts": status["active_alerts"],
    }


@app.get("/engines/{engine_id}/status")
async def get_engine_status(engine_id: str):
    """Get status of a specific engine."""
    if engine_id not in monitor.engines:
        raise HTTPException(status_code=404, detail=f"Engine {engine_id} not found")
    
    engine = monitor.engines[engine_id]
    return {
        "status": "success",
        "engine": engine.to_dict(),
    }


@app.get("/engines/consensus/k-value")
async def get_consensus_k_value():
    """Get overall system K-value (consensus coherence)."""
    status = monitor.get_current_status()
    
    # Calculate K-value from all engines
    engine_statuses = list(status["engines"].values())
    k_values = [e["k_value"] for e in engine_statuses]
    
    if not k_values:
        overall_k = 0.0
    else:
        overall_k = sum(k_values) / len(k_values)
    
    return {
        "status": "success",
        "overall_k_value": overall_k,
        "individual_k_values": {
            eid: e["k_value"] for eid, e in status["engines"].items()
        },
        "consensus_status": "CONVERGED" if overall_k >= 0.99 else "DIVERGING",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/health-check/history")
async def get_health_history(limit: int = 100):
    """Get recent health check history."""
    history = monitor.get_health_history(limit=limit)
    return {
        "status": "success",
        "count": len(history),
        "history": history,
    }


@app.get("/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary for visualization."""
    status = monitor.get_current_status()
    history = monitor.get_health_history(limit=10)
    
    engines = status["engines"]
    
    healthy = sum(1 for e in engines.values() if e["status"] == "healthy")
    degraded = sum(1 for e in engines.values() if e["status"] == "degraded")
    unhealthy = sum(1 for e in engines.values() if e["status"] == "unhealthy")
    
    avg_k = sum(e["k_value"] for e in engines.values()) / len(engines) if engines else 0
    
    return {
        "status": "success",
        "summary": {
            "total_engines": len(engines),
            "healthy_count": healthy,
            "degraded_count": degraded,
            "unhealthy_count": unhealthy,
            "overall_k_value": avg_k,
            "active_alerts": len(status["active_alerts"]),
        },
        "engines": {
            eid: {
                "name": e["engine_name"],
                "status": e["status"],
                "k_value": e["k_value"],
                "response_time_ms": e["response_time_ms"],
                "recovery_attempts": e["recovery_attempts"],
            }
            for eid, e in engines.items()
        },
        "recent_trend": [
            {
                "check_id": h["check_id"],
                "timestamp": h["timestamp"],
                "k_value": h["overall_k_value"],
                "healthy": h["healthy_count"],
            }
            for h in history
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/engine/{engine_id}/remediate")
async def remediate_engine(engine_id: str):
    """Manually trigger remediation for an engine."""
    if engine_id not in monitor.engines:
        raise HTTPException(status_code=404, detail=f"Engine {engine_id} not found")
    
    engine = monitor.engines[engine_id]
    action = await monitor._remediate_engine(engine_id, engine)
    
    return {
        "status": "success",
        "message": action,
        "engine_id": engine_id,
    }


@app.post("/maintenance/run-weekly")
async def run_weekly_maintenance():
    """Manually trigger weekly maintenance."""
    results = await monitor.weekly_maintenance()
    
    return {
        "status": "success",
        "message": "Weekly maintenance completed",
        "results": results,
    }


@app.get("/alerts")
async def get_active_alerts():
    """Get all active alerts."""
    return {
        "status": "success",
        "count": len(monitor.active_alerts),
        "alerts": monitor.active_alerts,
    }


@app.delete("/alerts/{engine_id}")
async def dismiss_alert(engine_id: str):
    """Dismiss alert for an engine."""
    if engine_id not in monitor.active_alerts:
        raise HTTPException(status_code=404, detail=f"No alert for engine {engine_id}")
    
    del monitor.active_alerts[engine_id]
    
    return {
        "status": "success",
        "message": f"Alert dismissed for {engine_id}",
    }


@app.get("/info")
async def system_info():
    """Get system information."""
    status = monitor.get_current_status()
    
    return {
        "service": "Engine Health Dashboard",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "engines_monitored": len(monitor.engines),
        "health_check_interval": "5 minutes",
        "maintenance_schedule": "Weekly (Sunday 2 AM UTC)",
        "current_status": status,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
