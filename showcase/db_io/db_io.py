from abc import ABC, abstractmethod

class DBIO(ABC):
    """
    Abstract base for database I/O. Different storage backends implements.
    """

    @abstractmethod
    def authenticate(self) -> None:
        """
        Perform provider-specific authentication (e.g. obtain API client, tokens).
        Subclasses must implement. Called by subclasses during initialization.
        """
        ...
    
    def upsert_table(self, dict_to_upsert)