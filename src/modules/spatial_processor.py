"""Spatial data processor for geographic context in RAG system"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

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

    COMPONENT_KEYWORDS = {
        "insulator": ["insulator", "insulators"],
        "earth_wire": ["earth wire", "ground wire"],
        "conductor": ["conductor", "phase conductors"],
        "fastener": ["bolt", "bolts", "fastener", "fasteners"],
        "connection_plate": ["connection plate", "connection plates"],
        "clamp": ["clamp", "clamps"],
        "steel_member": ["steel", "bracing", "member", "members"],
        "foundation": ["foundation", "ground rod", "grounding system"],
    }

    DEFECT_KEYWORDS = {
        "corrosion": ["corrosion", "rust"],
        "loose_fastener": ["loose fastener", "loose fasteners", "loose bolt", "loose bolts", "loosening"],
        "insulator_degradation": ["insulator degradation", "tracking", "puncture", "contamination"],
        "vibration": ["vibration", "resonance"],
        "fault": ["fault", "overvoltage"],
        "pollution": ["pollution", "moisture ingress"],
    }

    SEVERITY_PATTERNS = {
        "critical": ["critical", "critical concern"],
        "high": ["medium-high", "high"],
        "medium": ["moderate", "medium"],
        "low": ["low", "good condition", "excellent"],
    }

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
            tower_match = re.search(r'tower[_\s-]+([a-z0-9]+)', text, re.IGNORECASE)
            if tower_match:
                tower_info['tower_id'] = tower_match.group(1).upper()

        # Extract line information
        if 'line' in text.lower():
            line_match = re.search(
                r'(?:transmission\s+line|line)\s*:\s*([^\n]+)',
                text,
                re.IGNORECASE
            )
            if line_match:
                tower_info['line_name'] = line_match.group(1).strip()

        return tower_info

    @classmethod
    def extract_structured_fields(cls, text: str) -> Dict:
        """Extract normalized structured fields needed for MVP retrieval."""
        normalized = " ".join(text.lower().split())
        tower_info = cls.extract_tower_info(text)
        coordinates = cls.extract_coordinates(text)
        inspection_dates = cls.extract_dates(text)
        latest_inspection = max(inspection_dates) if inspection_dates else None
        risk_level = cls.extract_risk_level(text)
        component_types = cls._extract_keyword_matches(normalized, cls.COMPONENT_KEYWORDS)
        defect_types = cls._extract_keyword_matches(normalized, cls.DEFECT_KEYWORDS)
        phases = cls.extract_phases(normalized)
        hotspot_flag = any(term in normalized for term in [
            "hotspot", "thermal anomaly", "abnormal heating"
        ])

        return {
            "tower_id": tower_info.get("tower_id"),
            "line_name": tower_info.get("line_name"),
            "coordinates": coordinates,
            "inspection_date": latest_inspection.isoformat() if latest_inspection else None,
            "component_types": component_types,
            "defect_types": defect_types,
            "phases": phases,
            "severity": risk_level,
            "hotspot_flag": hotspot_flag,
            "condition_summary": cls.extract_condition_summary(text),
        }

    @staticmethod
    def extract_dates(text: str) -> List[datetime]:
        """Extract ISO dates from free text."""
        matches = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        dates = []
        for value in matches:
            try:
                dates.append(datetime.strptime(value, "%Y-%m-%d"))
            except ValueError:
                continue
        return dates

    @classmethod
    def extract_risk_level(cls, text: str) -> Optional[str]:
        """Normalize severity/risk level from document text."""
        normalized = " ".join(text.lower().split())
        explicit_match = re.search(
            r"current risk level:\s*([a-z-]+)",
            normalized,
            re.IGNORECASE
        )
        if explicit_match:
            return cls._normalize_severity(explicit_match.group(1))

        for severity, patterns in cls.SEVERITY_PATTERNS.items():
            if any(pattern in normalized for pattern in patterns):
                return severity
        return None

    @staticmethod
    def extract_phases(normalized_text: str) -> List[str]:
        """Extract and normalize phase references."""
        aliases = {
            "phase a": "R",
            "phase b": "Y",
            "phase c": "B",
            "r phase": "R",
            "y phase": "Y",
            "b phase": "B",
        }
        phases = []
        for pattern, normalized in aliases.items():
            if pattern in normalized_text and normalized not in phases:
                phases.append(normalized)
        return phases

    @staticmethod
    def extract_condition_summary(text: str) -> str:
        """Create a compact summary from the most relevant condition section."""
        for marker in [
            "recent observations",
            "recent condition",
            "critical issues",
            "risk assessment",
        ]:
            pattern = re.compile(
                rf"{marker}\s*:?(.*?)(?:adjacent towers:|monitoring plan:|$)",
                re.IGNORECASE | re.DOTALL
            )
            match = pattern.search(text)
            if match:
                return " ".join(match.group(1).split())[:300]
        return " ".join(text.split())[:300]

    @classmethod
    def parse_query_filters(cls, query_text: str) -> Dict:
        """Infer structured filters from a natural language query."""
        normalized = " ".join(query_text.lower().split())
        filters = {}

        phases = cls.extract_phases(normalized)
        if phases:
            filters["phase"] = phases[0]

        component_matches = cls._extract_keyword_matches(normalized, cls.COMPONENT_KEYWORDS)
        if component_matches:
            filters["component_type"] = component_matches[0]

        defect_matches = cls._extract_keyword_matches(normalized, cls.DEFECT_KEYWORDS)
        if defect_matches:
            filters["defect_type"] = defect_matches[0]

        severity = cls.extract_risk_level(normalized)
        if severity:
            filters["severity"] = severity

        if "hotspot" in normalized or "thermal" in normalized:
            filters["hotspot_flag"] = True

        tower_match = re.search(r"tower\s+([a-z0-9]+)", normalized, re.IGNORECASE)
        if tower_match:
            filters["tower_id"] = tower_match.group(1).upper()

        return filters

    @classmethod
    def _extract_keyword_matches(
        cls,
        normalized_text: str,
        keyword_map: Dict[str, List[str]]
    ) -> List[str]:
        matches = []
        for key, patterns in keyword_map.items():
            if any(pattern in normalized_text for pattern in patterns):
                matches.append(key)
        return matches

    @staticmethod
    def _normalize_severity(value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned == "medium-high":
            return "high"
        if cleaned == "moderate":
            return "medium"
        return cleaned

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
        structured_fields = SpatialMetadataExtractor.extract_structured_fields(content)
        metadata = {
            "coordinates": coordinates or structured_fields.get("coordinates"),
            "tower_info": SpatialMetadataExtractor.extract_tower_info(content),
            "tower_id": structured_fields.get("tower_id"),
            "line_name": structured_fields.get("line_name"),
            "component_types": structured_fields.get("component_types", []),
            "defect_types": structured_fields.get("defect_types", []),
            "phases": structured_fields.get("phases", []),
            "severity": structured_fields.get("severity"),
            "inspection_date": structured_fields.get("inspection_date"),
            "hotspot_flag": structured_fields.get("hotspot_flag", False),
            "condition_summary": structured_fields.get("condition_summary", ""),
            "content_length": len(content),
            "has_spatial_context": (coordinates or structured_fields.get("coordinates")) is not None
        }
        
        return metadata
