from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base

class IrrigationHistory(Base):
    __tablename__ = "irrigation_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    volume_liters: Mapped[float] = mapped_column(Float, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trigger_source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field: Mapped["Field"] = relationship("Field", back_populates="irrigation_history")

    # Time-series Index
    __table_args__ = (
        Index("idx_irrigation_field_time", "field_id", "start_time"),
    )

    def __repr__(self):
        return f"<IrrigationHistory(id={self.id}, field_id={self.field_id}, volume={self.volume_liters}L, trigger='{self.trigger_source}')>"
