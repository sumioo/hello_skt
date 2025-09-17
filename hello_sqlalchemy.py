from typing import Optional, List
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, func, and_, or_, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session, selectinload
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Team(Base):
    __tablename__ = "team"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), index=True)
    headquarters = Column(String(200))
    
    heroes = relationship("Hero", back_populates="team")

class HeroJoinedTeam(Base):
    __tablename__ = "hero_joined_team"
    
    hero_id = Column(Integer, ForeignKey("hero.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("nb_team.id"), primary_key=True)
    is_active = Column(Boolean, default=True)
    
    hero = relationship("Hero", back_populates="nb_team_links")
    team = relationship("NBTeam", back_populates="hero_links")

class NBTeam(Base):
    __tablename__ = "nb_team"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), index=True)
    
    hero_links = relationship("HeroJoinedTeam", back_populates="team")

class TeacherStudent(Base):
    __tablename__ = "teacher_student"
    
    teacher_id = Column(Integer, ForeignKey("teacher.id"), primary_key=True)
    hero_id = Column(Integer, ForeignKey("hero.id"), primary_key=True)

class Teacher(Base):
    __tablename__ = "teacher"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    
    students = relationship("Hero", secondary="teacher_student", back_populates="teachers")

class Hero(Base):
    __tablename__ = "hero"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    secret_name = Column(String(100))
    age = Column(Integer, nullable=True)
    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=True)
    
    team = relationship("Team", back_populates="heroes")
    teachers = relationship("Teacher", secondary="teacher_student", back_populates="students")
    nb_team_links = relationship("HeroJoinedTeam", back_populates="hero")
    
    def __str__(self):
        return f'<{self.id}>:{self.name}'

class HeroOut(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    display_name: str
    created_at: str

# 数据库配置
engine = create_engine("mysql+pymysql://root:qwer4321@localhost:3306/mydbx", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_all_tables():
    Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()

def add_heros(session: Session):
    """添加英雄数据"""
    heroes = [
        Hero(name="Deadpond", secret_name="Dive Wilson"),
        Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
        Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
    ]
    session.add_all(heroes)
    session.commit()
    return heroes

def get_heros(session: Session):
    """获取所有英雄"""
    return session.query(Hero).all()

def get_hero_by_name(session: Session, name: str):
    """根据名称获取英雄"""
    return session.query(Hero).filter(Hero.name == name).first()

def update_hero(session: Session, hero_id: int, age: int):
    """更新英雄年龄"""
    hero = session.query(Hero).filter(Hero.id == hero_id).first()
    if hero:
        hero.age = age
        session.commit()
    return hero

def update_heros(session: Session, ids: List[int], age: int):
    """批量更新英雄年龄"""
    session.query(Hero).filter(Hero.id.in_(ids)).update({"age": age}, synchronize_session=False)
    session.commit()

def batch_update_by_condition(session: Session, condition, update_dict: dict):
    """根据条件批量更新"""
    session.query(Hero).filter(condition).update(update_dict, synchronize_session=False)
    session.commit()

def delete_hero(session: Session, hero_id: int):
    """删除英雄"""
    hero = session.query(Hero).filter(Hero.id == hero_id).first()
    if hero:
        session.delete(hero)
        session.commit()
    return hero

def create_heroes(session: Session):
    """创建英雄数据"""
    print("Creating hero data...")
    heroes = [
        Hero(name="Deadpond", secret_name="Dive Wilson"),
        Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
        Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
    ]
    session.add_all(heroes)
    session.commit()
    print("Heroes created:")
    for hero in heroes:
        print(f"ID: {hero.id}, Name: {hero.name}")
    return heroes

def test_not_commit(session: Session):
    """测试未提交的事务"""
    hero = Hero(name="Test Hero", secret_name="Test Secret")
    session.add(hero)
    print(f"Hero added but not committed: {hero}")

def select_specific_columns(session: Session):
    """选择特定列查询"""
    return session.query(Hero.name, Hero.age).all()

def test_order_by_limit_offset(session: Session):
    """测试排序、限制和偏移"""
    return session.query(Hero).order_by(Hero.age.desc()).limit(2).offset(1).all()

def test_pagination(session: Session, page: int = 1, page_size: int = 2):
    """分页查询"""
    total = session.query(func.count(Hero.id)).scalar()
    heroes = session.query(Hero).order_by(Hero.id).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "heroes": heroes,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

def test_use_func(session: Session):
    """使用 SQL 函数"""
    result = session.query(
        func.count(Hero.id).label("total"),
        func.avg(Hero.age).label("avg_age"),
        func.max(Hero.age).label("max_age"),
        func.min(Hero.age).label("min_age")
    ).filter(Hero.age.isnot(None)).one()
    
    return {
        "total": result.total,
        "avg_age": float(result.avg_age) if result.avg_age else None,
        "max_age": result.max_age,
        "min_age": result.min_age
    }

def test_using_and(session: Session):
    """使用 AND 条件查询"""
    return session.query(Hero).filter(and_(Hero.age > 30, Hero.name.like("%Man%"))).all()

def create_teams(session: Session):
    """创建团队数据"""
    teams = [
        Team(name="Preventers", headquarters="Sharp Tower"),
        Team(name="Z-Force", headquarters="Sister Margaret's Bar")
    ]
    session.add_all(teams)
    session.commit()
    return teams

def test_select_related(session: Session):
    """关联查询"""
    # 内连接
    inner_join = session.query(Hero, Team).join(Team, Hero.team_id == Team.id).all()
    
    # 左外连接
    left_join = session.query(Hero, Team).outerjoin(Team, Hero.team_id == Team.id).all()
    
    return {"inner_join": inner_join, "left_join": left_join}

def test_select_related_2(session: Session):
    """使用 selectinload 预加载关联数据"""
    heroes = session.query(Hero).options(selectinload(Hero.team)).all()
    return heroes

def test_update_relate(session: Session):
    """更新关联数据"""
    hero = session.query(Hero).filter(Hero.name == "Rusty-Man").first()
    team = session.query(Team).filter(Team.name == "Preventers").first()
    
    if hero and team:
        hero.team_id = team.id
        session.commit()
    
    return hero

def test_m_2_m(session: Session):
    """测试多对多关系"""
    teacher = Teacher(name="Professor X")
    hero = session.query(Hero).filter(Hero.name == "Spider-Boy").first()
    
    if hero:
        teacher.students.append(hero)
        session.add(teacher)
        session.commit()
    
    return teacher

def test_m_2_m_related(session: Session):
    """测试多对多关联查询"""
    return session.query(Teacher).options(selectinload(Teacher.students)).all()

def test_m2m_with_extradata(session: Session):
    """测试带额外数据的多对多关系"""
    # 创建 NBTeam
    nb_team = NBTeam(name="Avengers")
    session.add(nb_team)
    session.commit()
    
    # 获取英雄
    hero = session.query(Hero).filter(Hero.name == "Deadpond").first()
    
    if hero:
        # 创建关联记录
        hero_joined_team = HeroJoinedTeam(hero_id=hero.id, team_id=nb_team.id, is_active=True)
        session.add(hero_joined_team)
        session.commit()
    
    # 预加载关联数据
    heroes_with_teams = session.query(Hero).options(
        selectinload(Hero.nb_team_links).selectinload(HeroJoinedTeam.team)
    ).all()
    
    return heroes_with_teams

def test_m2m_2(session: Session):
    """另一种多对多查询方式"""
    return session.query(HeroJoinedTeam).options(
        selectinload(HeroJoinedTeam.hero),
        selectinload(HeroJoinedTeam.team)
    ).all()

from sqlalchemy import select
def test_use_scalar(session: Session):
    """测试使用 scalar 方法"""
    heros = session.execute(select(Hero.id, Hero.name).where(Hero.name == "Spider-Boy")).all()
    print(heros, heros[0].name, '\n')

    heros = session.execute(select(Hero.id, Hero.name).where(Hero.name == "Spider-Boy")).scalar()
    print(heros)

    heros = session.execute(select(Hero.id, Hero.name).where(Hero.name == "Spider-Boy")).scalars()
    print(heros, '\n')

    heros = session.execute(select(Hero.id, Hero.name).where(Hero.name == "Spider-Boy")).scalars(index=0).fetchall()
    print(heros, '\n')

    heros = session.execute(select(Hero).where(Hero.name == "Spider-Boy")).all()
    print(heros, '\n')

    heros = session.execute(select(Hero).where(Hero.name == "Spider-Boy")).scalars().all()
    print(heros, '\n')

if __name__ == "__main__":
    # 创建所有表
    create_all_tables()
    
    # 获取会话
    session = get_session()
    create_heroes(session)
    create_teams(session)
    test_use_scalar(session)