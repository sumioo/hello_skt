from sqlmodel import Field, Session, SQLModel, create_engine, select, func, or_, and_, Relationship
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    heroes: list["Hero"] = Relationship(back_populates="team")


class HeroJoinedTeam(SQLModel, table=True):
    hero_id: int = Field(foreign_key="hero.id", primary_key=True)
    team_id: int = Field(foreign_key="nb_team.id", primary_key=True)
    is_active: bool = Field(default=True)

    hero: "Hero" = Relationship(back_populates="nb_team_links")
    team: "NBTeam" = Relationship(back_populates="hero_links")

class NBTeam(SQLModel, table=True):
    __tablename__ = "nb_team"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    hero_links: list[HeroJoinedTeam] = Relationship(back_populates="team")

class TeacherStudent(SQLModel, table=True):
    teacher_id: int = Field(foreign_key="teacher.id", primary_key=True)
    hero_id: int = Field(foreign_key="hero.id", primary_key=True)

class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    students: list["Hero"] = Relationship(back_populates="teachers", link_model=TeacherStudent)


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None
    team_id: int | None = Field(default=None, foreign_key="team.id", ondelete="CASCADE")
    
    team: Team | None = Relationship(back_populates="heroes")

    teachers: list[Teacher] = Relationship(back_populates="students", link_model=TeacherStudent)

    nb_team_links: list[HeroJoinedTeam] = Relationship(back_populates="hero")


    def __str__(self) -> str:
        return f'<{self.id}>:{self.name}'


class HeroOut(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    display_name: str  # 新增字段
    created_at: str  # 新增字段

# hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
# hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
# hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

engine = create_engine("mysql+pymysql://root:qwer4321@localhost:3306/mydbx", echo=True)
# print(SQLModel.metadata.tables)

def create_all_table():
    SQLModel.metadata.create_all(engine)

def add_heros():
    with Session(engine) as session: #隐式开启事务
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.commit()

def get_heros():
    with Session(engine) as session:
        heros = session.exec(select(Hero)).all()
        return heros

def get_hero_by_name(name):
    with Session(engine) as session:
        hero = session.exec(select(Hero).where(Hero.name == name)).first()
        return hero

def update_hero(hero):
    with Session(engine) as session:
        session.add(hero)
        session.commit()

def update_heros(heros):
    with Session(engine) as session:
        for hero in heros:
            session.add(hero)
        session.commit()

def batch_update_by_condition(update_values, condition):
    from sqlalchemy import update
    with Session(engine) as session:
        stmt = update(Hero).where(condition).values(**update_values)
        result = session.execute(stmt)
        rowcount = result.rowcount
        session.commit()
        return rowcount

def delete_hero(hero):
    with Session(engine) as session:
        session.delete(hero)
        session.commit()

def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    print("Before interacting with the database")
    print("Hero 1:", hero_1)
    print("Hero 2:", hero_2)
    print("Hero 3:", hero_3)

    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)

        print("After adding to the session")
        print("Hero 1:", hero_1)
        print("Hero 2:", hero_2)
        print("Hero 3:", hero_3)

        session.commit()

        print("After committing the session")
        print("Hero 1:", hero_1)
        print("Hero 2:", hero_2)
        print("Hero 3:", hero_3)

        print("After committing the session, show IDs")
        print("Hero 1 ID:", hero_1.id)
        print("Hero 2 ID:", hero_2.id)
        print("Hero 3 ID:", hero_3.id)

        print("After committing the session, show names")
        print("Hero 1 name:", hero_1.name)
        print("Hero 2 name:", hero_2.name)
        print("Hero 3 name:", hero_3.name)

        session.refresh(hero_1)
        session.refresh(hero_2)
        session.refresh(hero_3)

        print("After refreshing the heroes")
        print("Hero 1:", hero_1)
        print("Hero 2:", hero_2)
        print("Hero 3:", hero_3)

    print("After the session closes")
    print("Hero 1:", hero_1)
    print("Hero 2:", hero_2)
    print("Hero 3:", hero_3)

def test_not_commit():
    hero = Hero(name="x1", secret_name="x1")
    with Session(engine) as session:
        session.add(hero)
        session.flush()
        print(hero.id)

    with Session(engine) as session:
        hero = session.exec(select(Hero).where(Hero.name == "x1")).first()
        print(hero)
        assert hero is not None

def select_specific_columns(fields):
    with Session(engine) as session:
        return session.exec(select(*fields)).all()

def test_order_by_limit_offset(order_bys, offset, limit):
    with Session(engine) as session:
        heros = session.exec(select(Hero.id, Hero.name).order_by(*order_bys).limit(limit).offset(offset)).all()
        print(heros)

def test_pagination(page: int, size: int):
    """
    Paginate heroes with total count
    Args:
        page: Current page number (1-based)
        size: Number of items per page
    Returns:
        tuple: (list of heroes for current page, total count, total pages)
    """
    with Session(engine) as session:
        # Calculate offset
        offset = (page - 1) * size
        
        # Get total count
        total = session.exec(select(func.count(Hero.id))).first()
        
        # Calculate total pages
        total_pages = (total + size - 1) // size
        
        # Get paginated results
        heroes = session.exec(
            select(Hero)
            .offset(offset)
            .limit(size)
        ).all()
        
        return {
            "items": heroes,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }
    # with Session(engine) as session:
    #     result = session.exec(select(func.count(Hero.id).label("total")).where(Hero.age > 40)).first()
    #     print(result, type(result)) # result 是int  3 <class 'int'>
    #     print(result.total) # total属性是没有的

def test_use_func():
    with Session(engine) as session:
        result = session.exec(select(
            func.count(Hero.id).label('total_heroes'),
            func.avg(Hero.age).label('average_age'),
            func.max(Hero.age).label('max_age'),
            func.min(Hero.age).label('min_age')
        )).first()
    print(result, type(result))
    print(f"总数: {result.total_heroes}")
    print(f"平均年龄: {result.average_age}")
    print(f"最大年龄: {result.max_age}")
    print(f"最小年龄: {result.min_age}")


def test_using_and():
    with Session(engine) as session:
        heros = session.exec(select(Hero).where(and_(Hero.secret_name.like("Dive%"), Hero.age > 40))).all()
        print(heros)


def create_teams():
    with Session(engine) as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")
        session.add(team_preventers)
        session.add(team_z_force)
        session.commit()


def test_select_related():
    with Session(engine) as session:
        heroes = session.exec(select(Hero, Team).where(Hero.team_id == Team.id)).all()
        # SELECT hero.id, hero.name, hero.secret_name, hero.age, hero.team_id,
        # team.id AS id_1, team.name AS name_1, team.headquarters 
        # FROM hero, team 
        # WHERE hero.team_id = team.id
        print(heroes[0])
        # (Hero(team_id=1, id=1, secret_name='Dive Wilson', age=200, name='Deadpond'), Team(id=1, headquarters='Sharp Tower', name='Preventers'))
        
        heroes = session.exec(select(Hero, Team).where(Hero.age > 50)).all()
        print(heroes)
        # SELECT hero.id, hero.name, hero.secret_name, hero.age, hero.team_id, team.id AS id_1, team.name AS name_1, team.headquarters 
        # FROM hero, team 
        # WHERE hero.age > %(age_1)s
        # 返回的是Hero和Team的笛卡尔积
        # [(Hero(team_id=1, id=1, secret_name='Dive Wilson', age=200, name='Deadpond'), Team(headquarters="Sister Margaret's Bar", id=2, name='Z-Force')), 
        # (Hero(team_id=1, id=1, secret_name='Dive Wilson', age=200, name='Deadpond'), Team(headquarters='Sharp Tower', id=1, name='Preventers'))]

        heros = session.exec(select(Hero, Team).join(Team).where(Hero.age > 12)).all()
        print(heros)
        
        # SELECT hero.id, hero.name, hero.secret_name, hero.age, hero.team_id, team.id AS id_1, team.name AS name_1, team.headquarters 
        # FROM hero 
        # INNER JOIN team ON team.id = hero.team_id 
        # WHERE hero.age > %(age_1)s
        # [(Hero(team_id=1, id=1, secret_name='Dive Wilson', age=200, name='Deadpond'), Team(headquarters='Sharp Tower', id=1, name='Preventers')), (Hero(team_id=2, id=3, secret_name='Tommy Sharp', age=38, name='Rusty-Man'), Team(headquarters="Sister Margaret's Bar", id=2, name='Z-Force')), (Hero(team_id=2, id=6, secret_name='Tommy Sharp', age=48, name='Rusty-Man'), Team(headquarters="Sister Margaret's Bar", id=2, name='Z-Force'))]

        heroes = session.exec(select(Hero, Team).join(Team, isouter=True).where(Hero.age > 12)).all()
        print(heroes)
        # SELECT hero.id, hero.name, hero.secret_name, hero.age, hero.team_id, team.id AS id_1, team.name AS name_1, team.headquarters 
        # FROM hero 
        # LEFT OUTER JOIN team ON team.id = hero.team_id 
        # WHERE hero.age > %(age_1)s
        # [(Hero(team_id=1, id=1, secret_name='Dive Wilson', age=200, name='Deadpond'), Team(id=1, headquarters='Sharp Tower', name='Preventers')), (Hero(team_id=2, id=3, secret_name='Tommy Sharp', age=38, name='Rusty-Man'), Team(id=2, headquarters="Sister Margaret's Bar", name='Z-Force')), (Hero(team_id=2, id=6, secret_name='Tommy Sharp', age=48, name='Rusty-Man'), Team(id=2, headquarters="Sister Margaret's Bar", name='Z-Force')), (Hero(team_id=None, id=8, secret_name='Tommy Sharp', age=48, name='Rasty-Man'), None)]

def test_select_related_2():
    with Session(engine) as session:
        heroes = session.exec(select(Hero).options(selectinload(Hero.team))).all()
        print(heroes[0].team)
        print(heroes[0].team.name)

        print("="*20)
    # SELECT hero.id, hero.name, hero.secret_name, hero.age, hero.team_id 
    # FROM hero
    # 2025-07-27 15:55:00,926 INFO sqlalchemy.engine.Engine [generated in 0.00006s] {}
    # 2025-07-27 15:55:00,931 INFO sqlalchemy.engine.Engine SELECT team.id AS team_id, team.name AS team_name, team.headquarters AS team_headquarters 
    # FROM team 
    # WHERE team.id IN (%(primary_keys_1)s, %(primary_keys_2)s)
    # 2025-07-27 15:55:00,931 INFO sqlalchemy.engine.Engine [generated in 0.00017s] {'primary_keys_1': 1, 'primary_keys_2': 2}
    # headquarters='Sharp Tower' id=1 name='Preventers'
        statement = select(Hero).where(Hero.name == "Spider-Boy").limit(1)
        result = session.exec(statement)
        hero_spider_boy = result.first()
        print(hero_spider_boy.team)

    print("="*20)
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy").limit(2)
        result = session.exec(statement)
        heroes = result.all()
        for hero in heroes:
            print(hero.team)
    # 2025-07-27 16:08:55,711 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    # 2025-07-27 16:08:55,711 INFO sqlalchemy.engine.Engine SELECT hero.id, hero.name, hero.secret_name, hero.age, hero.team_id 
    # FROM hero 
    # WHERE hero.name = %(name_1)s 
    #  LIMIT %(param_1)s
    # 2025-07-27 16:08:55,711 INFO sqlalchemy.engine.Engine [cached since 0.003083s ago] {'name_1': 'Spider-Boy', 'param_1': 2}
    # 2025-07-27 16:08:55,713 INFO sqlalchemy.engine.Engine SELECT team.id AS team_id, team.name AS team_name, team.headquarters AS team_headquarters 
    # FROM team 
    # WHERE team.id = %(pk_1)s
    # 2025-07-27 16:08:55,713 INFO sqlalchemy.engine.Engine [generated in 0.00007s] {'pk_1': 1}
    # headquarters='Sharp Tower' id=1 name='Preventers'
    # 2025-07-27 16:08:55,714 INFO sqlalchemy.engine.Engine SELECT team.id AS team_id, team.name AS team_name, team.headquarters AS team_headquarters 
    # FROM team 
    # WHERE team.id = %(pk_1)s
    # 2025-07-27 16:08:55,714 INFO sqlalchemy.engine.Engine [cached since 0.001072s ago] {'pk_1': 5}
    # headquarters='X-MAN' id=5 name='X-Police'

    print('\n',"="*20, '\n')
    with Session(engine) as session:
        statement = select(Team).where(Team.id.in_([1, 2])).limit(1)
        result = session.exec(statement)
        teams = result.all()
        for team in teams:
            print(team.heroes)


def test_update_relate():
    with Session(engine) as session:
        hero_spider_boy = session.exec(
            select(Hero).where(Hero.name == "Spider-Boy")
        ).first()

        preventers_team = session.exec(
            select(Team).where(Team.name == "Preventers")
        ).one()

        print("Hero Spider-Boy:", hero_spider_boy)
        print("Preventers Team:", preventers_team)
        print("Preventers Team Heroes:", preventers_team.heroes)

        hero_spider_boy.team = None

        print("Spider-Boy without team:", hero_spider_boy)

        print("Preventers Team Heroes again:", preventers_team.heroes)
        #Preventers Team Heroes again: [Hero(name='Deadpond', secret_name='Dive Wilson', age=200, id=1, team_id=1)]

        session.add(hero_spider_boy)
        session.commit()
        print("After committing")

        session.refresh(hero_spider_boy)
        print("Spider-Boy after commit:", hero_spider_boy)

        print("Preventers Team Heroes after commit:", preventers_team.heroes)


def test_m_2_m():
    with Session(engine) as session:
        teacher = session.exec(select(Teacher).where(Teacher.name == "gonduola")).first()
        hero = session.exec(select(Hero).where(Hero.name == "Deadpond")).first()
        teacher.students.append(hero)
        session.commit()

def test_m_2_m_related():        
    with Session(engine) as session:
        teacher = session.exec(select(Teacher).where(Teacher.name == "gonduola")).first()
        print("\nteacher.students:", teacher.students)
        hero = session.exec(select(Hero).where(Hero.name == "Rusty-Man")).first()
        print("\nhero.teachers:", hero.teachers)

def test_m2m_with_extradata():
    with Session(engine) as session:
        hero = session.exec(select(Hero).where(Hero.name == "Deadpond")).first()
        print("\nhero.nb_team_links:", hero.nb_team_links)
        print("\nhero.nb_team_links[0].team:", hero.nb_team_links[0].team)

        print("="*20, "selectinload", "="*20)

        hero = session.exec(
            select(Hero)
            .where(Hero.name == "Deadpond")
            .options(selectinload(Hero.nb_team_links).selectinload(HeroJoinedTeam.team))
        ).first()
        print("\nhero.nb_team_links:", hero.nb_team_links)
        print("\nhero.nb_team_links[0].team:", hero.nb_team_links[0].team)

if __name__ == "__main__":
    # test m 2 m with extra data
    test_m2m_with_extradata()

    # test m 2 m select
    # test_m_2_m_related()

    # test m 2 m
    # test_m_2_m()

    # create tablea
    # create_all_table()

    # create_teams()

    # get
    # heros = get_heros()
    # print(heros)


    # hero = get_hero_by_name("Deadpond")
    # print(hero)

    # update
    # hero = get_hero_by_name("Deadpond")
    # hero.age = 200
    # update_hero(hero)

    # from sqlalchemy import and_
    # affected_rows = batch_update_by_condition(
    #     {"age": Hero.age - 5},
    #     and_(Hero.age != None, Hero.age > 40)
    # )
    # print(f"更新了 {affected_rows} 条记录")

    # create_heroes()

    # scalars() 方法用于：
    # - 提取第一列的值 ：当查询返回多列时，只取第一列
    # - 简化结果结构 ：将复杂的行结构转换为简单的值序列
    # - 类型转换 ：将数据库行对象转换为 Python 对象

    # with Session(engine) as session:
    #     heros_unscalar = session.execute(select(Hero).limit(2)).all()
    #     print("未使用scalars方法：", heros_unscalar)
    #     heroes = session.execute(select(Hero).limit(2)).scalars().all()
    #     print("使用scalars方法：", heroes)
    #     heros_autoscalar = session.exec(select(Hero).limit(2)).all()
    #     print("使用exec方法：", heros_autoscalar)

    # 假设 HeroOut 只比 Hero 多 display_name 字段
    # hero = Hero(id=1, name="Deadpond", secret_name="Dive Wilson", age=30)
    # extra = {"display_name": "超级Deadpond", "created_at": "2025-01-01"}
    # hero_out = HeroOut(**hero.model_dump(exclude={"secret_name"}), **extra)
    # print(hero_out)

    # 测试是否是隐式开启事务
    # test_not_commit()

    # 测试查询指定列
    # heroes = select_specific_columns([Hero.id, Hero.name, Hero.age])
    # print(heroes)

    # 测试排序分页
    # test_order_by_limit_offset([Hero.id], 1, 2)
    # test_order_by_limit_offset([Hero.id.desc()], 0, 2)
    # test_order_by_limit_offset([Hero.id.desc(), Hero.name], 0, 10)

    # 测试分页
    # result = test_pagination(1, 2)
    # print(result)

    # 测试使用func
    # test_use_func()

    # 测试使用and和前缀匹配
    # test_using_and()

    # test select related
    # test_select_related()

    # test_select_related_2()

    # test_update_relate()
