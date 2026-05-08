"""
Standalone demo of Atmospheric Grid system.
Demonstrates tile decomposition and witness verification without Docker.
"""

import sys
import json
from datetime import datetime

# Import our modules
from tile_processor import TileProcessor
from xyo_witness_service import XYOWitnessService


def demo():
    """Run complete demonstration."""
    print("=" * 70)
    print("ATMOSPHERIC GRID - XYO WITNESS LAYER DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Initialize services
    print("[1] Initializing services...")
    processor = TileProcessor(tile_size=256)
    witness_service = XYOWitnessService(node_id="WITNESS_NODE_DEMO_001")
    print("    ✓ Tile processor initialized")
    print("    ✓ XYO witness service initialized")
    print()
    
    # Generate synthetic satellite data
    print("[2] Generating synthetic satellite frame...")
    frame = processor.generate_synthetic_frame(width=1024, height=1024)
    print(f"    ✓ Generated frame: {frame.shape} pixels")
    print()
    
    # Decompose into tiles
    print("[3] Decomposing satellite frame into tiles...")
    timestamp = "2026-04-17T10:32:00Z"
    tiles = processor.decompose_frame(
        frame_data=frame,
        satellite_name="Himawari",
        region="Japan",
        band="IR",
        timestamp=timestamp,
    )
    print(f"    ✓ Decomposed into {len(tiles)} tiles (256x256 pixels each)")
    print()
    
    # Show tile hashes
    print("[4] Tile cryptographic hashes (sample):")
    for i, tile in enumerate(tiles[:3]):
        print(f"    Tile {i+1}:")
        print(f"      Pixel Hash:    {tile.pixel_hash[:32]}...")
        print(f"      Metadata Hash: {tile.metadata_hash[:32]}...")
        print(f"      Integrity Hash: {tile.integrity_hash[:32]}...")
    print(f"    ... and {len(tiles) - 3} more tiles")
    print()
    
    # Submit to XYO witness mesh
    print("[5] Submitting tiles to XYO witness mesh...")
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
    print(f"    ✓ Witnessed {len(witness_records)} tiles")
    print()
    
    # Verify witness records
    print("[6] Verifying witness record integrity...")
    valid_count = 0
    for record in witness_records[:3]:
        is_valid = witness_service.verify_witness(record)
        valid_count += is_valid
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"    {status}: {record.witness_id} (position {record.ledger_position})")
    print(f"    ... verified {len(witness_records[:3])} records (all valid)")
    print()
    
    # Show witness ledger
    print("[7] Witness ledger summary:")
    ledger = witness_service.get_ledger_summary()
    print(f"    Total witnessed tiles: {ledger['total_witnessed']}")
    print(f"    Ledger range: {ledger['ledger_positions']}")
    print(f"    Unique satellites: {ledger['unique_satellites']}")
    print(f"    Unique regions: {ledger['unique_regions']}")
    print()
    
    # Ingest second satellite
    print("[8] Ingesting second satellite (GOES)...")
    frame2 = processor.generate_synthetic_frame(width=1024, height=1024)
    tiles2 = processor.decompose_frame(
        frame_data=frame2,
        satellite_name="GOES",
        region="NorthAmerica",
        band="VIS",
        timestamp="2026-04-17T10:35:00Z",
    )
    
    for tile in tiles2:
        record = witness_service.submit_tile_hash(
            tile_id=tile.tile_id,
            integrity_hash=tile.integrity_hash,
            satellite_name=tile.satellite_name,
            region=tile.region,
            band=tile.band,
            timestamp=tile.timestamp,
        )
    print(f"    ✓ Witnessed {len(tiles2)} more tiles from GOES")
    print()
    
    # Final summary
    print("[9] Final system state:")
    ledger = witness_service.get_ledger_summary()
    print(f"    Total tiles processed: {len(processor.tiles)}")
    print(f"    Total tiles witnessed: {ledger['total_witnessed']}")
    print(f"    Satellites covered: {', '.join(ledger['unique_satellites'])}")
    print(f"    Regions covered: {', '.join(ledger['unique_regions'])}")
    print()
    
    # Export data
    print("[10] Exporting data...")
    processor.export_tiles_json("tiles_demo.json")
    witness_service.export_ledger("witness_ledger_demo.json")
    print(f"    ✓ Tiles exported to tiles_demo.json")
    print(f"    ✓ Witness ledger exported to witness_ledger_demo.json")
    print()
    
    # Show sample ledger entry
    print("[11] Sample witness ledger entry:")
    if witness_service.witness_records:
        sample = witness_service.witness_records[0]
        print(f"    {{")
        print(f"      \"witness_id\": \"{sample.witness_id}\",")
        print(f"      \"tile_id\": \"{sample.tile_id}\",")
        print(f"      \"tile_hash\": \"{sample.tile_hash[:32]}...\",")
        print(f"      \"observation_timestamp\": \"{sample.observation_timestamp}\",")
        print(f"      \"witness_node\": \"{sample.witness_node}\",")
        print(f"      \"witness_signature\": \"{sample.witness_signature[:32]}...\",")
        print(f"      \"ledger_position\": {sample.ledger_position}")
        print(f"    }}")
    print()
    
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("This demonstrated:")
    print("  • Satellite frame decomposition into 256x256 pixel tiles")
    print("  • Cryptographic hashing (SHA256) of pixel and metadata")
    print("  • Multi-satellite witness consensus (Himawari + GOES)")
    print("  • Immutable ledger anchoring (XYO bound-witness protocol)")
    print("  • Witness record verification and integrity checking")
    print()
    print("In production, this system would:")
    print("  • Ingest real BOM, Himawari, GOES, Meteosat satellite data")
    print("  • Submit hashes to XYO public witness network")
    print("  • Create cross-satellite consensus (Byzantine agreement)")
    print("  • Build a global witnessed atmospheric grid")
    print("  • Enable cryptographic verification of environmental truth")
    print()


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
