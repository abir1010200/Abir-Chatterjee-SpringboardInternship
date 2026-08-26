from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type = Column(String(50), nullable=False)  # e.g., Wheat, Tomato, Maize, Cotton, Rice
    growth_stage = Column(String(50), nullable=False, default="Initial")  # Initial, Vegetative, Flowering, Mid-Season, Late-Season, Harvest
    planted_date = Column(Date, nullable=False, default=date.today)
    expected_harvest_date = Column(Date, nullable=True)
    kc_factor = Column(Float, nullable=False, default=1.0)  # Crop water demand factor Kc
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field = relationship("Field", back_populates="crops")

    def __repr__(self):
        return f"<Crop(id={self.id}, field_id={self.field_id}, type='{self.crop_type}', stage='{self.growth_stage}')>"
