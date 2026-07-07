"""Resolved bookable catalog selection — canonical input to calendar and availability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

SelectionType = Literal["normal", "full_package"]
PolicyProfile = Literal["single", "full_package"]

POLICY_PROFILE_BY_SELECTION_TYPE: dict[SelectionType, PolicyProfile] = {
    "full_package": "full_package",
    "normal": "single",
}


@dataclass(frozen=True)
class BookableSelection:
    selection_type: SelectionType
    public_id: UUID
    slug: str
    name: str
    duration_minutes: int
    policy_profile: PolicyProfile

    @classmethod
    def from_parts(
        cls,
        *,
        selection_type: SelectionType,
        public_id: UUID,
        slug: str,
        name: str,
        duration_minutes: int,
    ) -> BookableSelection:
        return cls(
            selection_type=selection_type,
            public_id=public_id,
            slug=slug,
            name=name,
            duration_minutes=duration_minutes,
            policy_profile=POLICY_PROFILE_BY_SELECTION_TYPE[selection_type],
        )

    def to_api_payload(self) -> dict:
        return {
            "selection_type": self.selection_type,
            "public_id": str(self.public_id),
            "slug": self.slug,
            "name": self.name,
            "duration_minutes": self.duration_minutes,
        }

    @property
    def calendar_layout_key(self) -> str:
        """Key used by calendar domain (`normal` | `full_package`)."""
        return self.selection_type
