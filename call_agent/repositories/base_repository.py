from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
import json
import os
from datetime import datetime

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository class for database operations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.file_path = os.path.join(data_dir, f"{self.get_collection_name()}.json")
        os.makedirs(data_dir, exist_ok=True)
        self._ensure_file_exists()
    
    @abstractmethod
    def get_collection_name(self) -> str:
        """Return the collection name for this repository"""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to model instance"""
        pass
    
    def _ensure_file_exists(self):
        """Ensure the data file exists"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]):
        """Save data to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create(self, entity: T) -> T:
        """Create a new entity"""
        data = self._load_data()
        entity_dict = entity.to_dict()
        data.append(entity_dict)
        self._save_data(data)
        return entity
    
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID"""
        data = self._load_data()
        for item in data:
            if item.get('id') == entity_id:
                return self.from_dict(item)
        return None
    
    def find_all(self) -> List[T]:
        """Find all entities"""
        data = self._load_data()
        return [self.from_dict(item) for item in data]
    
    def update(self, entity: T) -> Optional[T]:
        """Update an existing entity"""
        data = self._load_data()
        for i, item in enumerate(data):
            if item.get('id') == entity.id:
                data[i] = entity.to_dict()
                self._save_data(data)
                return entity
        return None
    
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID"""
        data = self._load_data()
        for i, item in enumerate(data):
            if item.get('id') == entity_id:
                del data[i]
                self._save_data(data)
                return True
        return False
    
    def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find entities by field value"""
        data = self._load_data()
        results = []
        for item in data:
            if item.get(field) == value:
                results.append(self.from_dict(item))
        return results
    
    def find_one_by_field(self, field: str, value: Any) -> Optional[T]:
        """Find one entity by field value"""
        results = self.find_by_field(field, value)
        return results[0] if results else None