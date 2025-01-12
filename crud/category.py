from typing import Type

from sqlalchemy.orm import Session
from models import Category
from schemas import CategoryCreate

categories = [
    {
        "name": "evil",
        "label": "😈 Злой",
        "color": "bg-red-600 hover:bg-red-700",
        "description": "Резкий и гневный смех, выражающий раздражение или фрустрацию. Может сопровождаться коварными комментариями."
    },
    {
        "name": "powerful",
        "label": "🐉 Дракон",
        "color": "bg-green-500 hover:bg-green-600",
        "description": "Громкий и мощный смех, демонстрирующий силу и величие, иногда вызывающий страх."
    },
    {
        "name": "rich",
        "label": "💰 Богатый",
        "color": "bg-yellow-500 hover:bg-yellow-600",
        "description": "Изысканный, уверенный смех, демонстрирующий статус, силу и решимость."
    },
    {
        "name": "poor",
        "label": "🥺 Бедный",
        "color": "bg-gray-400 hover:bg-gray-500",
        "description": "Скромный и искренний смех."
    },
    {
        "name": "poor2",
        "label": "🥴 Бомж",
        "color": "bg-gray-400 hover:bg-gray-500",
        "description": "Смех бомжа отражающий жизненные трудности с позитивом."
    },
    {
        "name": "non_human",
        "label": "🤖 Робот",
        "color": "bg-blue-500 hover:bg-blue-600",
        "description": "Механический и экзотический смех, отличающийся от земных форм, иногда с электронными искажениями."
    },
    {
        "name": "magical",
        "label": "🧚‍♀️ Фея",
        "color": "bg-pink-500 hover:bg-pink-600",
        "description": "Тёплый, добродушный и волшебный смех, ассоциирующийся с радостью и праздниками."
    },
    {
        "name": "friendly",
        "label": "🧝‍♂️ Гном/Бармен",
        "color": "bg-green-500 hover:bg-green-600",
        "description": "Весёлый и добродушный смех, характерный для дружелюбных персонажей."
    },
    {
        "name": "witch_clown",
        "label": "🧙‍♀️ Ведьма",
        "color": "bg-purple-500 hover:bg-purple-600",
        "description": "Злобный и насмешливый смех, часто сопровождающий хитрые планы или саркастические комментарии."
    },
    {
        "name": "pirate",
        "label": "🏴‍☠️ Пират",
        "color": "bg-gray-800 hover:bg-gray-900",
        "description": "Грубый и хриплый смех с нотками дерзости и уверенности. Йохохо"
    },
    {
        "name": "child",
        "label": "👶 Ребёнок",
        "color": "bg-yellow-300 hover:bg-yellow-400",
        "description": "Милый и нежный смех, вызывающий умиление и улыбки, характерный для детей."
    },
    {
        "name": "chicken",
        "label": "🐔 Курица",
        "color": "bg-yellow-300 hover:bg-yellow-400",
        "description": "Неряшливый и смешной смех, напоминающий кукареканье или куриный звук."
    },
    {
        "name": "alcohol",
        "label": "🍻 Алкогольный",
        "color": "bg-orange-500 hover:bg-orange-600",
        "description": "Расслабленный и иногда неустойчивый смех, возникающий под воздействием алкоголя."
    },
    {
        "name": "unsorted",
        "label": "Без сортировки",
        "color": "bg-gray-500 hover:bg-gray-600",
        "description": ""
    }
]

def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(
        name=data.name,
        label=data.label,
        color=data.color,
        description=data.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.query(Category).filter(Category.name == name).first()

def get_categories(db: Session) -> list[Type[Category]]:
    return db.query(Category).all()

def insert_categories(db: Session):
    existing_categories = set([category.name for category in db.query(Category.name).all()])
    for category in categories:
        if category["name"] not in existing_categories:
            # If the category doesn't exist, insert it
            db_category = Category(
                name=category["name"],
                label=category["label"],
                color=category["color"],
                description=category["description"]
            )
            db.add(db_category)
            print(f"Inserting category: {category['name']}")
    db.commit()