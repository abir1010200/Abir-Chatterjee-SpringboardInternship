from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base

class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(50), nullable=False)
    growth_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="Initial")
    planted_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    kc_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field: Mapped["Field"] = relationship("Field", back_populates="crops")

    def __repr__(self):
        return f"<Crop(id={self.id}, field_id={self.field_id}, type='{self.crop_type}', stage='{self.growth_stage}')>"
