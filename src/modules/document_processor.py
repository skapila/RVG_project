"""Document processing module for RVG Project"""

import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document loading and preprocessing"""

    SUPPORTED_FORMATS = {".txt", ".pdf", ".docx", ".md", ".csv", ".json"}

    def __init__(self):
        """Initialize DocumentProcessor"""
        logger.info("DocumentProcessor initialized")

    def load_documents(self, path):
        """Load documents from a given path"""
        documents = []
        path = Path(path)

        if path.is_file():
            loaded = self._load_single_document(path)
            documents.extend(loaded if isinstance(loaded, list) else [loaded])
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix in self.SUPPORTED_FORMATS:
                    loaded = self._load_single_document(file_path)
                    documents.extend(loaded if isinstance(loaded, list) else [loaded])

        valid_documents = [doc for doc in documents if doc]
        logger.info(f"Loaded {len(valid_documents)} documents")
        return valid_documents

    def _load_single_document(self, file_path):
        """Load a single document"""
        file_path = Path(file_path)
        logger.debug(f"Loading: {file_path}")

        try:
            if file_path.suffix == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif file_path.suffix == ".md":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif file_path.suffix == ".csv":
                return self._load_csv_records(file_path)
            elif file_path.suffix == ".json":
                return self._load_json_records(file_path)
            else:
                content = f"Content from {file_path.name}"

            return {"path": str(file_path), "content": content, "metadata": {}}
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def preprocess(self, documents):
        """Preprocess documents"""
        processed = []
        for doc in documents:
            if doc:
                # Remove extra whitespace
                content = " ".join(doc["content"].split())
                processed.append({
                    "path": doc["path"],
                    "content": content,
                    "metadata": doc.get("metadata", {}),
                })
        return processed

    def _load_csv_records(self, file_path):
        """Load structured tower records from a CSV file."""
        records = []
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for index, row in enumerate(reader, start=1):
                metadata = {key: value for key, value in row.items() if value not in (None, "")}
                records.append({
                    "path": f"{file_path}#row{index}",
                    "content": self._structured_record_to_text(metadata),
                    "metadata": metadata,
                })
        return records

    def _load_json_records(self, file_path):
        """Load structured tower records from a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        if isinstance(payload, dict):
            records = payload.get("records", [])
        elif isinstance(payload, list):
            records = payload
        else:
            raise ValueError(f"Unsupported JSON structure in {file_path}")

        loaded = []
        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                continue
            loaded.append({
                "path": f"{file_path}#record{index}",
                "content": self._structured_record_to_text(record),
                "metadata": record,
            })
        return loaded

    @staticmethod
    def _structured_record_to_text(record):
        """Create a text representation from structured tower metadata."""
        lines = [
            f"Tower {record.get('tower_id', 'UNKNOWN')}",
            f"Line: {record.get('line_name', 'Unknown Line')}",
            f"Circuit: {record.get('circuit_id', 'Unknown')}",
        ]

        if record.get("latitude") and record.get("longitude"):
            lines.append(f"Coordinates: {record['latitude']}, {record['longitude']}")

        field_labels = [
            ("inspection_date", "Inspection Date"),
            ("severity", "Severity"),
            ("component_type", "Component"),
            ("phase", "Phase"),
            ("defect_type", "Defect"),
            ("thermal_max", "Thermal Max"),
            ("hotspot_flag", "Hotspot"),
            ("earth_wire_condition", "Earth Wire Condition"),
            ("tower_condition_summary", "Tower Condition Summary"),
            ("observation_note", "Observation Note"),
            ("remark", "Remark"),
            ("image_path", "Image Path"),
        ]
        for key, label in field_labels:
            value = record.get(key)
            if value not in (None, ""):
                lines.append(f"{label}: {value}")

        return "\n".join(lines)
