"""WordPress integration exceptions."""

class WordPressException(Exception):
    """Base exception for WordPress integration."""
    pass

class WordPressConnectionError(WordPressException):
    """Raised when unable to connect to WordPress."""
    pass

class WordPressAuthError(WordPressException):
    """Raised when authentication fails."""
    pass

class WordPressSyncError(WordPressException):
    """Raised when sync operation fails."""
    pass
