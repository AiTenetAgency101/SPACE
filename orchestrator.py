"""
Atmospheric Grid Orchestrator
Coordinates satellite frame decomposition and XYO witness submission.
Exposes FastAPI endpoints for querying witnessed atmospheric data.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from tile_processor import TileProcessor
from xyo_witness_service import XYOWitnessService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Atmospheric Grid",
    description="Witnessed satellite atmospheric data layer powered by XYO",
    version="1.0.0",
)

# Global services
tile_processor = TileProcessor(tile_size=512)
witness_service = XYOWitnessService(node_id="WITNESS_NODE_GLOBAL_001")


@app.on_event("startup")
async def startup():
    """Initialize system on startup."""
    logger.info("Starting Atmospheric Grid service...")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Atmospheric Grid",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/ingest/satellite-frame")
async def ingest_satellite_frame(
    satellite_name: str,
    region: str,
    band: str,
    timestamp: str,
    width: int = 2048,
    height: int = 2048,
):
    """
    Ingest a satellite frame, decompose into tiles, and submit to witness mesh.
    
    This endpoint simulates the complete flow:
    1. Receive satellite frame (or generate synthetic for demo)
    2. Decompose into tiles
    3. Compute cryptographic hashes
    4. Submit to XYO witness mesh
    5. Return witness records
    """
    try:
        # Generate synthetic frame for demo
        # In production, this would accept actual satellite data
        frame = tile_processor.generate_synthetic_frame(width, height)
        
        # Decompose into tiles
        tiles = tile_processor.decompose_frame(
            frame_data=frame,
            satellite_name=satellite_name,
            region=region,
            band=band,
            timestamp=timestamp,
        )
        logger.info(f"Decomposed frame into {len(tiles)} tiles")
        
        # Submit all tiles to witness mesh
        witness_records = []
        for tile in tiles:
            record = witness_service.submit_tile_hash(
                tile_id=tile.tile_id,
                integrity_hash=tile.integrity_hash,
                satellite_name=tile.satellite_name,
                region=tile.region,
                band=tile.band,
                timestamp=tile.timestamp,
            )
            witness_records.append(record)
        
        return {
            "status": "success",
            "satellite": satellite_name,
            "region": region,
            "band": band,
            "tiles_processed": len(tiles),
            "tiles_witnessed": len(witness_records),
            "sample_witness_records": [
                {
                    "witness_id": r.witness_id,
                    "tile_id": r.tile_id,
                    "tile_hash": r.tile_hash[:16] + "...",
                    "witness_signature": r.witness_signature[:16] + "...",
                    "ledger_position": r.ledger_position,
                }
                for r in witness_records[:3]
            ],
        }
    
    except Exception as e:
        logger.error(f"Error ingesting satellite frame: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tiles/summary")
async def get_tiles_summary():
    """Get summary of all processed tiles."""
    summary = tile_processor.get_tile_summary()
    return {
        "status": "success",
        "tiles": summary,
    }


@app.get("/witness/ledger-summary")
async def get_ledger_summary():
    """Get summary of witness ledger."""
    summary = witness_service.get_ledger_summary()
    return {
        "status": "success",
        "witness_ledger": summary,
    }


@app.get("/witness/verify/{witness_id}")
async def verify_witness_record(witness_id: str):
    """Verify a specific witness record by ID."""
    try:
        # Find record by witness_id
        record = next(
            (r for r in witness_service.witness_records if r.witness_id == witness_id),
            None,
        )
        
        if not record:
            raise HTTPException(status_code=404, detail=f"Witness record {witness_id} not found")
        
        is_valid = witness_service.verify_witness(record)
        
        return {
            "status": "success",
            "witness_id": witness_id,
            "valid": is_valid,
            "tile_id": record.tile_id,
            "tile_hash": record.tile_hash,
            "observation_timestamp": record.observation_timestamp,
            "witness_node": record.witness_node,
            "ledger_position": record.ledger_position,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying witness: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/query/witnessed-tiles")
async def query_witnessed_tiles(
    satellite: str = None,
    region: str = None,
    limit: int = 10,
):
    """Query witnessed tiles by satellite or region."""
    records = witness_service.witness_records
    
    # Filter by satellite if specified
    if satellite:
        records = [r for r in records if satellite in r.tile_id]
    
    # Filter by region if specified
    if region:
        records = [r for r in records if region in r.tile_id]
    
    # Limit results
    records = records[:limit]
    
    return {
        "status": "success",
        "query_filters": {"satellite": satellite, "region": region},
        "results_count": len(records),
        "witnessed_tiles": [
            {
                "witness_id": r.witness_id,
                "tile_id": r.tile_id,
                "tile_hash": r.tile_hash[:16] + "...",
                "observation_timestamp": r.observation_timestamp,
                "ledger_position": r.ledger_position,
            }
            for r in records
        ],
    }


@app.post("/export/tiles")
async def export_tiles(filename: str = "tiles.json"):
    """Export all processed tiles."""
    tile_processor.export_tiles_json(filename)
    return {
        "status": "success",
        "message": f"Tiles exported to {filename}",
        "count": len(tile_processor.tiles),
    }


@app.post("/export/ledger")
async def export_ledger(filename: str = "witness_ledger.json"):
    """Export witness ledger."""
    witness_service.export_ledger(filename)
    return {
        "status": "success",
        "message": f"Ledger exported to {filename}",
        "count": len(witness_service.witness_records),
    }


@app.get("/info")
async def system_info():
    """Get system information."""
    return {
        "service": "Atmospheric Grid - XYO Witness Layer",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tile_processor": {
            "total_tiles": len(tile_processor.tiles),
            "summary": tile_processor.get_tile_summary(),
        },
        "witness_service": {
            "total_witnessed": len(witness_service.witness_records),
            "ledger_position": witness_service.ledger_position,
            "summary": witness_service.get_ledger_summary(),
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
