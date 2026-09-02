from sqlalchemy import select

from modules.shared.database.connection import get_session
from modules.shared.database.models import Queue
from modules.shared.defaults.Queue import Item_Queue


def add_queue_item(item: Item_Queue) -> bool:

    statement = select(Queue).where(
        Queue.source_file == item.source_file,
        Queue.source_file_row == item.source_file_row,
    )

    with next(get_session()) as db:
        result = db.execute(statement).scalar_one_or_none()

    if not result:
        db.add(Queue(**item.model_dump()))
        db.commit()
        return True

    return False
