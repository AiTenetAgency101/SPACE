"""
XYO Witness Service
Submits satellite tile hashes to the XYO bound-witness mesh for cryptographic anchoring.
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WitnessRecord:
    """Record of a tile witnessed by XYO mesh."""
    witness_id: str
    tile_id: str
    tile_hash: str
    observation_timestamp: str
    witness_node: str
    witness_signature: str
    ledger_position: int


class XYOWitnessService:
    """
    Service that submits satellite tile hashes to XYO bound-witness mesh.
    
    This is the bridge between atmospheric data (tiles) and cryptographic verification (XYO).
    Each tile hash is witnessed by distributed XYO nodes, creating a tamper-evident record.
    """
    
    def __init__(self, node_id: str = "WITNESS_NODE_001"):
        """
        Initialize XYO witness service.
        
        Args:
            node_id: Identifier for this witness node
        """
        self.node_id = node_id
        self.witness_records: List[WitnessRecord] = []
        self.ledger_position = 0
    
    def submit_tile_hash(
        self,
        tile_id: str,
        integrity_hash: str,
        satellite_name: str,
        region: str,
        band: str,
        timestamp: str,
    ) -> WitnessRecord:
        """
        Submit a tile hash to the XYO witness mesh.
        
        This simulates XYO bound-witness protocol:
        1. Tile hash is submitted
        2. Witness nodes observe and timestamp
        3. Nodes create bound-witness signatures
        4. Hash is anchored to immutable ledger
        
        Args:
            tile_id: Unique identifier for the tile
            integrity_hash: SHA256 hash of tile (pixel + metadata)
            satellite_name: Source satellite name
            region: Geographic region
            band: Spectral band
            timestamp: Original observation timestamp
        
        Returns:
            WitnessRecord with witness signature and ledger position
        """
        observation_time = datetime.utcnow().isoformat() + "Z"
        
        # Create witness signature (simulates XYO HMAC protocol)
        # In production, this would use XYO's cryptographic key infrastructure
        signature_input = f"{tile_id}{integrity_hash}{observation_time}{self.node_id}"
        witness_signature = hashlib.sha256(signature_input.encode()).hexdigest()
        
        # Increment ledger position
        self.ledger_position += 1
        
        # Create witness record
        record = WitnessRecord(
            witness_id=f"WIT_{self.ledger_position:06d}",
            tile_id=tile_id,
            tile_hash=integrity_hash,
            observation_timestamp=observation_time,
            witness_node=self.node_id,
            witness_signature=witness_signature,
            ledger_position=self.ledger_position,
        )
        
        self.witness_records.append(record)
        
        logger.info(
            f"Witnessed tile {tile_id} at position {self.ledger_position}: {witness_signature[:16]}..."
        )
        
        return record
    
    def batch_submit_tiles(self, tiles_json_path: str) -> List[WitnessRecord]:
        """
        Load tiles from JSON and submit all to witness mesh.
        
        Args:
            tiles_json_path: Path to tiles.json from tile processor
        
        Returns:
            List of WitnessRecord objects
        """
        with open(tiles_json_path, 'r') as f:
            tiles_data = json.load(f)
        
        records = []
        for tile in tiles_data:
            record = self.submit_tile_hash(
                tile_id=tile['tile_id'],
                integrity_hash=tile['integrity_hash'],
                satellite_name=tile['satellite_name'],
                region=tile['region'],
                band=tile['band'],
                timestamp=tile['timestamp'],
            )
            records.append(record)
        
        logger.info(f"Submitted {len(records)} tiles to witness mesh")
        return records
    
    def verify_witness(self, witness_record: WitnessRecord) -> bool:
        """
        Verify that a witness record is valid (signature matches hash).
        
        Args:
            witness_record: WitnessRecord to verify
        
        Returns:
            True if signature is valid, False otherwise
        """
        # Reconstruct the signature
        signature_input = f"{witness_record.tile_id}{witness_record.tile_hash}{witness_record.observation_timestamp}{witness_record.witness_node}"
        reconstructed_sig = hashlib.sha256(signature_input.encode()).hexdigest()
        
        is_valid = reconstructed_sig == witness_record.witness_signature
        logger.info(f"Witness {witness_record.witness_id} verification: {'VALID' if is_valid else 'INVALID'}")
        return is_valid
    
    def get_ledger_summary(self) -> Dict:
        """Get summary of witnessed tiles."""
        if not self.witness_records:
            return {"count": 0, "records": []}
        
        unique_satellites = set(r.tile_id.split('_')[0] for r in self.witness_records)
        unique_regions = set(r.tile_id.split('_')[2] for r in self.witness_records)
        
        return {
            "total_witnessed": len(self.witness_records),
            "ledger_positions": (1, self.ledger_position),
            "unique_satellites": list(unique_satellites),
            "unique_regions": list(unique_regions),
            "sample_records": [asdict(r) for r in self.witness_records[:3]],
        }
    
    def export_ledger(self, output_path: str) -> None:
        """Export witness ledger as JSON."""
        ledger_data = [asdict(record) for record in self.witness_records]
        with open(output_path, 'w') as f:
            json.dump(ledger_data, f, indent=2)
        logger.info(f"Ledger exported to {output_path}")


if __name__ == "__main__":
    # Example usage
    witness_service = XYOWitnessService(node_id="WITNESS_NODE_AU_001")
    
    # Simulate witnessing tiles
    sample_records = []
    for i in range(5):
        tile_id = f"Himawari_IR_Japan_20260417T1032Z_{i*512}_{i*512}"
        integrity_hash = hashlib.sha256(f"tile_data_{i}".encode()).hexdigest()
        
        record = witness_service.submit_tile_hash(
            tile_id=tile_id,
            integrity_hash=integrity_hash,
            satellite_name="Himawari",
            region="Japan",
            band="IR",
            timestamp="2026-04-17T10:32:00Z",
        )
        sample_records.append(record)
    
    print("Witness Ledger Summary:")
    print(json.dumps(witness_service.get_ledger_summary(), indent=2))
    
    # Verify records
    for record in sample_records:
        witness_service.verify_witness(record)
    
    # Export ledger
    witness_service.export_ledger("witness_ledger.json")
    print("\nLedger exported to witness_ledger.json")
