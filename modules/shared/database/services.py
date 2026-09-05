from sqlalchemy import select

from modules.shared.database.connection import get_session
from modules.shared.database.models import ArtistsModel, MusicsModel, Queue
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
        .outerjoin(MusicsModel, Queue.track_uri == MusicsModel.reference)
        .where(Queue.status == 'in_queue', MusicsModel.reference.is_(None))
        .group_by(Queue.track_uri)
    )

    with next(get_session()) as db:
        result: list[str] = db.execute(statement).scalars().all()

    return result


def add_data_music_artist(item: MusicsModel):
    with next(get_session()) as db:
        for artist in item.artists:
            statement = select(ArtistsModel).where(ArtistsModel.reference == artist.reference)
            result = db.execute(statement).scalar_one_or_none()

            if not result:
                db.add(artist)
            else:
                continue

        statement = select(MusicsModel).where(MusicsModel.reference == item.reference)
        result = db.execute(statement).scalar_one_or_none()

        if not result:
            db.add(item)
            db.commit()
            return True

        return False
