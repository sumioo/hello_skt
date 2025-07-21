from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional

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
    with Session(engine) as session:
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

class HeroOut(SQLModel):
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

    # with Session(engine) as session:
    #     heroes = session.execute(select(Hero).limit(2)).scalars().all()
    #     print(heroes)

    # 假设 HeroOut 只比 Hero 多 display_name 字段
    hero = Hero(id=1, name="Deadpond", secret_name="Dive Wilson", age=30)
    extra = {"display_name": "超级Deadpond", "created_at": "2025-01-01"}
    hero_out = HeroOut(**hero.model_dump(exclude={"secret_name"}), **extra)
    print(hero_out)
