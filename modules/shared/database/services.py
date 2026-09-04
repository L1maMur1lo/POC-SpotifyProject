from sqlalchemy import select

from modules.shared.database.connection import get_session
from modules.shared.database.models import Musics, Queue
from modules.shared.defaults.Validator import QueueVal


def add_queue_item(item: QueueVal) -> bool:

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


def missing_tracks() -> list[str]:

    statement = (
        select(Queue.track_uri)
        .outerjoin(Musics, Queue.track_uri == Musics.reference)
        .where(Queue.status == 'in_queue', Musics.reference.is_(None))
        .group_by(Queue.track_uri)
    )

    with next(get_session()) as db:
        result: list[str] = db.execute(statement).scalars().all()

    return result


def add_music() -> bool:
    pass
