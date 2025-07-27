from sqlmodel import Field, Session, SQLModel, create_engine, select, func
from typing import Optional
from pydantic import BaseModel

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None


hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

engine = create_engine("mysql+pymysql://root:qwer4321@localhost:3306/mydbx", echo=True)
print(SQLModel.metadata.tables)

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
        session.merge(hero)
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
    with Session(engine) as session:
        result = session.exec(select(func.count(Hero.id).label("total")).where(Hero.age > 40)).first()
        print(result, type(result)) # result 是int  3 <class 'int'>
        print(result.total) # total属性是没有的

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

class HeroOut(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    display_name: str  # 新增字段
    created_at: str  # 新增字段


if __name__ == "__main__":
    # heros = get_heros()
    # print(heros)
    # hero = get_hero_by_name("Deadpond")
    # print(hero)
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
    result = test_pagination(1, 2)
    print(result)

    # 测试使用func
    # test_use_func()


