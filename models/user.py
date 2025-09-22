from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """
    Entity representing file ownership and operation context.
    """
    user_id: str
    display_name: str
    created_at: Optional[datetime] = None
    session_context: Optional[dict] = None

    def __post_init__(self):
        """Validate user data after initialization."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        self.validate()

    def validate(self):
        """Validate user fields according to business rules."""
        # User ID validation
        if not self.user_id:
            raise ValueError("User ID required and unique")

        # Display name validation
        if not self.display_name:
            raise ValueError("Display name required for audit trails")

    def to_dict(self) -> dict:
        """Convert user to dictionary representation."""
        return {
            'user_id': self.user_id,
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'session_context': self.session_context
        }

    @classmethod
    def from_session_context(cls, user_id: str, display_name: str, session_data: dict = None) -> 'User':
        """Create User instance from session context."""
        return cls(
            user_id=user_id,
            display_name=display_name,
            session_context=session_data or {}
        )

    def update_session_context(self, context_data: dict):
        """Update session context with new data."""
        if self.session_context is None:
            self.session_context = {}
        self.session_context.update(context_data)

    def get_context_value(self, key: str, default=None):
        """Get value from session context."""
        if self.session_context is None:
            return default
        return self.session_context.get(key, default)

    def is_authenticated(self) -> bool:
        """Check if user has valid authentication context."""
        # For now, return True if user_id exists
        # Future: check session tokens, authentication status
        return bool(self.user_id)

    def get_audit_info(self) -> dict:
        """Get user information for audit logging."""
        return {
            'user_id': self.user_id,
            'display_name': self.display_name,
            'timestamp': datetime.utcnow().isoformat()
        }