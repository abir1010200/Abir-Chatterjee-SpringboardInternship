from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class IrrigationHistory(Base):
    __tablename__ = "irrigation_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    volume_liters = Column(Float, nullable=False)  # Total volume discharged in Liters
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    trigger_source = Column(String(50), default="manual", nullable=False)  # manual, automated_ml, rule_based
    status = Column(String(20), default="completed", nullable=False)  # completed, in_progress, aborted
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field = relationship("Field", back_populates="irrigation_history")

    # Time-series Index
    __table_args__ = (
        Index("idx_irrigation_field_time", "field_id", "start_time"),
    )

    def __repr__(self):
        return f"<IrrigationHistory(id={self.id}, field_id={self.field_id}, volume={self.volume_liters}L, trigger='{self.trigger_source}')>"
