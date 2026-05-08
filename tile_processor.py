"""
Satellite Tile Processor
Decomposes satellite frames into sub-frames (tiles), computes cryptographic hashes,
and prepares them for XYO witness submission.
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Tuple
import numpy as np
from pathlib import Path


@dataclass
class SatelliteTile:
    """Represents a witnessed atmospheric sub-frame."""
    satellite_name: str
    region: str
    band: str
    timestamp: str
    tile_id: str
    pixel_hash: str
    metadata_hash: str
    integrity_hash: str
    dimensions: Tuple[int, int]
    data_source: str


class TileProcessor:
    """Decomposes satellite frames into tiles and computes hashes."""
    
    def __init__(self, tile_size: int = 512):
        """
        Initialize tile processor.
        
        Args:
            tile_size: Dimension of each tile (tile_size x tile_size pixels)
        """
        self.tile_size = tile_size
        self.tiles: List[SatelliteTile] = []
    
    def decompose_frame(
        self,
        frame_data: np.ndarray,
        satellite_name: str,
        region: str,
        band: str,
        timestamp: str,
    ) -> List[SatelliteTile]:
        """
        Decompose a satellite frame into tiles and compute hashes.
        
        Args:
            frame_data: Satellite image data (numpy array)
            satellite_name: Name of satellite (BOM, Himawari, GOES, Meteosat)
            region: Geographic region (e.g., "Sydney", "Japan", "NorthAmerica")
            band: Spectral band (VIS, IR, WV, etc.)
            timestamp: ISO 8601 timestamp
        
        Returns:
            List of SatelliteTile objects with computed hashes
        """
        h, w = frame_data.shape[:2]
        tiles = []
        
        for y in range(0, h, self.tile_size):
            for x in range(0, w, self.tile_size):
                # Extract tile
                y_end = min(y + self.tile_size, h)
                x_end = min(x + self.tile_size, w)
                tile_pixels = frame_data[y:y_end, x:x_end]
                
                # Compute pixel hash (SHA256 of pixel data)
                pixel_bytes = tile_pixels.tobytes()
                pixel_hash = hashlib.sha256(pixel_bytes).hexdigest()
                
                # Compute metadata hash
                metadata = {
                    "satellite": satellite_name,
                    "region": region,
                    "band": band,
                    "timestamp": timestamp,
                    "tile_position": [x, y],
                    "tile_dimensions": [x_end - x, y_end - y],
                }
                metadata_json = json.dumps(metadata, sort_keys=True)
                metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
                
                # Compute integrity hash (combines pixel + metadata)
                combined = pixel_hash + metadata_hash
                integrity_hash = hashlib.sha256(combined.encode()).hexdigest()
                
                # Generate tile ID
                tile_id = f"{satellite_name}_{band}_{region}_{timestamp.replace(':', '-').replace('Z', '')}_{x}_{y}"
                
                tile = SatelliteTile(
                    satellite_name=satellite_name,
                    region=region,
                    band=band,
                    timestamp=timestamp,
                    tile_id=tile_id,
                    pixel_hash=pixel_hash,
                    metadata_hash=metadata_hash,
                    integrity_hash=integrity_hash,
                    dimensions=(x_end - x, y_end - y),
                    data_source=f"frame[{y}:{y_end}, {x}:{x_end}]",
                )
                
                tiles.append(tile)
        
        self.tiles.extend(tiles)
        return tiles
    
    def generate_synthetic_frame(
        self,
        width: int = 2048,
        height: int = 2048,
    ) -> np.ndarray:
        """
        Generate synthetic satellite frame for testing.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels
        
        Returns:
            Numpy array representing satellite data
        """
        # Simulate atmospheric data with noise and patterns
        frame = np.random.randint(0, 256, (height, width), dtype=np.uint8)
        
        # Add some structure (cloud patterns)
        y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
        pattern = (np.sin(x_coords / 100) + np.cos(y_coords / 100)) * 50 + 128
        frame = (frame * 0.5 + pattern * 0.5).astype(np.uint8)
        
        return frame
    
    def export_tiles_json(self, output_path: str) -> None:
        """Export all tiles as JSON for downstream processing."""
        tiles_data = [asdict(tile) for tile in self.tiles]
        with open(output_path, 'w') as f:
            json.dump(tiles_data, f, indent=2)
    
    def get_tile_summary(self) -> dict:
        """Get summary of processed tiles."""
        if not self.tiles:
            return {"count": 0, "tiles": []}
        
        return {
            "count": len(self.tiles),
            "satellites": list(set(t.satellite_name for t in self.tiles)),
            "regions": list(set(t.region for t in self.tiles)),
            "bands": list(set(t.band for t in self.tiles)),
            "sample_integrity_hashes": [t.integrity_hash for t in self.tiles[:3]],
        }


if __name__ == "__main__":
    # Example usage
    processor = TileProcessor(tile_size=512)
    
    # Generate synthetic satellite data
    frame = processor.generate_synthetic_frame(2048, 2048)
    
    # Decompose into tiles
    timestamp = datetime.utcnow().isoformat() + "Z"
    tiles = processor.decompose_frame(
        frame_data=frame,
        satellite_name="Himawari",
        region="Japan",
        band="IR",
        timestamp=timestamp,
    )
    
    print(f"Processed {len(tiles)} tiles")
    print(f"Summary: {processor.get_tile_summary()}")
    
    # Export for witness submission
    processor.export_tiles_json("tiles.json")
    print("Tiles exported to tiles.json")
