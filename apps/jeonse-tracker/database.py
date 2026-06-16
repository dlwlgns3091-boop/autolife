from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///./jeonse.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    evaluations = relationship("Evaluation", back_populates="user")
    weights = relationship("UserWeight", back_populates="user")


class PreferenceItem(Base):
    __tablename__ = "preference_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # 'common' or user_id (stored as string for flexibility)
    scope = Column(String, nullable=False, default="common")
    default_weight = Column(Float, nullable=False, default=3.0)
    weights = relationship("UserWeight", back_populates="item")
    evaluations = relationship("Evaluation", back_populates="item")


class UserWeight(Base):
    __tablename__ = "user_weights"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("preference_items.id"), nullable=False)
    weight = Column(Float, nullable=False)
    user = relationship("User", back_populates="weights")
    item = relationship("PreferenceItem", back_populates="weights")


class House(Base):
    __tablename__ = "houses"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, nullable=False)
    deposit = Column(Integer, nullable=False)  # 만원 단위
    area = Column(Float, nullable=True)  # 평
    rooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    monthly_cost = Column(Integer, nullable=True)  # 만원 단위
    link = Column(Text, nullable=True)
    memo = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="관심")  # 관심/방문예정/방문완료/제외
    evaluations = relationship("Evaluation", back_populates="house")


class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("preference_items.id"), nullable=False)
    score = Column(Float, nullable=False, default=3.0)  # 1~5
    house = relationship("House", back_populates="evaluations")
    user = relationship("User", back_populates="evaluations")
    item = relationship("PreferenceItem", back_populates="evaluations")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed users
        if db.query(User).count() == 0:
            db.add_all([User(name="소희"), User(name="지훈")])
            db.commit()

        # Seed preference items
        if db.query(PreferenceItem).count() == 0:
            items = [
                PreferenceItem(name="고정비용(월 지출)", scope="common", default_weight=5.0),
                PreferenceItem(name="방 넓이", scope="소희", default_weight=4.0),
                PreferenceItem(name="직주근접", scope="지훈", default_weight=4.0),
                PreferenceItem(name="집 컨디션(구조/연식)", scope="common", default_weight=3.0),
                PreferenceItem(name="평수", scope="common", default_weight=3.0),
            ]
            db.add_all(items)
            db.commit()

        # Seed user weights from default_weight
        if db.query(UserWeight).count() == 0:
            users = db.query(User).all()
            items = db.query(PreferenceItem).all()
            for user in users:
                for item in items:
                    db.add(UserWeight(user_id=user.id, item_id=item.id, weight=item.default_weight))
            db.commit()
    finally:
        db.close()
