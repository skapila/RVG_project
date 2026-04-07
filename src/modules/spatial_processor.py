"""Spatial data processor for geographic context in RAG system"""

import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SpatialChunker:
    """Handles spatial chunking of documents with geographic metadata"""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize SpatialChunker
        
        Args:
            chunk_size: Tokens per chunk
            overlap: Overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        logger.info(f"SpatialChunker initialized: size={chunk_size}, overlap={overlap}")

    def chunk_document(
        self,
        content: str,
        coordinates: Optional[Tuple[float, float]] = None,
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Chunk document while preserving spatial metadata
        
        Args:
            content: Document text
            coordinates: (latitude, longitude) tuple
            metadata: Additional metadata (tower_id, line_name, etc.)
            
        Returns:
            List of chunks with spatial metadata
        """
        chunks = []
        tokens = content.split()
        
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            chunk_tokens = tokens[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_tokens)
            
            chunk_dict = {
                "content": chunk_text,
                "token_count": len(chunk_tokens),
                "position": i // self.chunk_size,
                "coordinates": coordinates,
                "metadata": metadata or {}
            }
            chunks.append(chunk_dict)
        
        logger.debug(f"Chunked document into {len(chunks)} segments")
        return chunks

    def chunk_by_region(
        self,
        documents: List[Dict],
        grid_cell_size: int = 1
    ) -> Dict[str, List[Dict]]:
        """
        Organize chunks by geographic grid cells
        
        Args:
            documents: List of document chunks with coordinates
            grid_cell_size: Grid cell size in degrees
            
        Returns:
            Dictionary mapping grid cell to documents
        """
        regional_chunks = {}
        
        for doc in documents:
            coords = doc.get("coordinates")
            if not coords:
                continue
                
            lat, lon = coords
            cell_key = (
                round(lat / grid_cell_size) * grid_cell_size,
                round(lon / grid_cell_size) * grid_cell_size
            )
            
            if cell_key not in regional_chunks:
                regional_chunks[cell_key] = []
            
            regional_chunks[cell_key].append(doc)
        
        logger.info(f"Organized into {len(regional_chunks)} geographic regions")
        return regional_chunks


class SpatialMetadataExtractor:
    """Extract and structure spatial metadata from documents"""

    @staticmethod
    def extract_coordinates(text: str) -> Optional[Tuple[float, float]]:
        """
        Extract coordinates from text
        
        Args:
            text: Document text
            
        Returns:
            (latitude, longitude) tuple or None
        """
        import re
        
        # Pattern: latitude, longitude
        pattern = r'[-+]?\d+\.?\d*[,\s]+[-+]?\d+\.?\d*'
        match = re.search(pattern, text)
        
        if match:
            coords = match.group().replace(',', ' ').split()
            try:
                lat, lon = float(coords[0]), float(coords[1])
                return (lat, lon)
            except (ValueError, IndexError):
                return None
        
        return None

    @staticmethod
    def extract_tower_info(text: str) -> Dict:
        """
        Extract tower-specific information
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with tower metadata
        """
        tower_info = {}
        
        # Extract tower ID
        if 'tower' in text.lower():
            import re
            tower_match = re.search(r'tower[_\s]+(\w+)', text, re.IGNORECASE)
            if tower_match:
                tower_info['tower_id'] = tower_match.group(1)
        
        # Extract line information
        if 'line' in text.lower():
            import re
            line_match = re.search(r'line[_\s]+(\w+)', text, re.IGNORECASE)
            if line_match:
                tower_info['line_name'] = line_match.group(1)
        
        return tower_info

    @staticmethod
    def create_spatial_metadata(
        content: str,
        coordinates: Optional[Tuple[float, float]] = None
    ) -> Dict:
        """
        Create comprehensive spatial metadata
        
        Args:
            content: Document content
            coordinates: Geographic coordinates
            
        Returns:
            Complete metadata dictionary
        """
        metadata = {
            "coordinates": coordinates,
            "tower_info": SpatialMetadataExtractor.extract_tower_info(content),
            "content_length": len(content),
            "has_spatial_context": coordinates is not None
        }
        
        return metadata
