"""
External Interface Definitions
Defines contracts for external interfaces used by leaf nodes.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InterfaceResult:
    """Result from external interface operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    bytes_transferred: int = 0


class FileInterface(ABC):
    """Abstract interface for file-based I/O."""

    @abstractmethod
    def read(self, path: str) -> InterfaceResult:
        """Read from file."""
        pass

    @abstractmethod
    def write(self, path: str, data: Any) -> InterfaceResult:
        """Write to file."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    def connect(self, connection_string: str) -> InterfaceResult:
        """Connect to database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from database."""
        pass

    @abstractmethod
    def query(self, sql: str, params: Optional[Dict] = None) -> InterfaceResult:
        """Execute query."""
        pass

    @abstractmethod
    def execute(self, sql: str, params: Optional[Dict] = None) -> InterfaceResult:
        """Execute non-query statement."""
        pass


class HTTPInterface(ABC):
    """Abstract interface for HTTP operations."""

    @abstractmethod
    def get(self, url: str, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP GET request."""
        pass

    @abstractmethod
    def post(self, url: str, data: Any, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP POST request."""
        pass

    @abstractmethod
    def put(self, url: str, data: Any, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP PUT request."""
        pass

    @abstractmethod
    def delete(self, url: str, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP DELETE request."""
        pass


class APIInterface(ABC):
    """Abstract interface for external API calls (e.g., LLM)."""

    @abstractmethod
    def call(self, endpoint: str, payload: Dict) -> InterfaceResult:
        """Call external API."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get API status."""
        pass
