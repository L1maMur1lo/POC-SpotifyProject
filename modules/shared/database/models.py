from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Queue(Base):
    """
    Tabela criada para administrar, os dados antes da inserção no banco
    """

    __tablename__ = 'queue'

    # Campo padrão
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # Link da track (contem o Id da track)
    track_uri: Mapped[str] = mapped_column(String, nullable=False)
    # Tempo de reprodução da musica durou em milisegundos
    ms_played: Mapped[int] = mapped_column(Integer, nullable=False)
    # Data e Hora do usuario
    ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Se o usuario estava online durante a reprodução
    offline: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Data e hora do usuario durante "offline" (timestamp)
    offline_ts: Mapped[Optional[BigInteger]] = mapped_column(BigInteger)
    # Arquivo de onde o dado foi extraido
    source_file: Mapped[str] = mapped_column(String)
    # Linha e Arquivo do arquivo de onde o dado foi extraido
    source_file_row: Mapped[int] = mapped_column(Integer)
    # Estado de processamento do item na fila
    status: Mapped[Optional[str]] = mapped_column(
        String, server_default='in_queue', init=False
    )


class ExecutionsModel(Base):
    """
    Tabela que registra as execuções do usuario
    """

    __tablename__ = 'executions'

    # Campo padrão
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # Chave estrangeira (musics - reference)
    music_reference: Mapped[str] = mapped_column(
        ForeignKey('musics.reference', ondelete='CASCADE', onupdate='CASCADE'), nullable=False
    )
    # Tempo de reprodução da musica durou em milisegundos
    ms_played: Mapped[int] = mapped_column(Integer, nullable=False)
    # Data e hora da reprodução
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Se o usuario estava online durante a reprodução
    offline: Mapped[Optional[bool]] = mapped_column(
        Boolean, server_default='false', default=False
    )
    # Origem do dado
    source: Mapped[Optional[str]] = mapped_column(String, default='')

    # Associando a musica a execução
    # (Many-to-One)
    music: Mapped[MusicsModel] = relationship(
        'MusicsModel', back_populates='executions', lazy='selectin', init=False
    )


# Tabela intermediaria de relação entre musicas e artistas
music_artist_association = Table(
    'music_artist_association',
    Base.metadata,
    Column('music_reference', String, ForeignKey('musics.reference'), primary_key=True),
    Column('artist_reference', String, ForeignKey('artists.reference'), primary_key=True),
)


class MusicsModel(Base):
    """
    Tabela contendo as informações das musicas
    """

    __tablename__ = 'musics'

    # Campo padrão
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # Id da track no spotify
    reference: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # "Nome" da track
    title: Mapped[str] = mapped_column(String, nullable=False)
    # Não tem necessidade pratica este campo, mas visualmente ele é importante
    names: Mapped[str] = mapped_column(String, nullable=False)
    # Duração em Milisegundos
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    # Link para a imagem do album
    album_img_url: Mapped[str] = mapped_column(String)

    # Lista de artistas (tabela)
    # (Many-to-Many)
    artists: Mapped[List[ArtistsModel]] = relationship(
        'ArtistsModel',
        secondary=music_artist_association,
        back_populates='musics',
        lazy='selectin',
        default_factory=list,
        init=False
    )

    # Associando uma lista de execuções para a musica
    # (One-to-Many)
    executions: Mapped[List[ExecutionsModel]] = relationship(
        'ExecutionsModel',
        back_populates='music',
        cascade='all, delete-orphan',
        default_factory=list,
    )

    @property
    def artists_names(self) -> List[str]:
        """
        Retorna dinamicamente a lista de nomes dos artistas vinculados a esta música.
        """
        return [artist.name for artist in self.artists]


class ArtistsModel(Base):
    """
    Tabela contendo as informações dos artistas
    """

    __tablename__ = 'artists'

    # Campo padrão
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # Id do artista no spotify
    reference: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # Nome do artista no spotify
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Link para a imagem do artista
    profile_img_url: Mapped[Optional[str]] = mapped_column(String)
    # Associando as musicas ao artista
    # (Many-to-Many)
    musics: Mapped[List[MusicsModel]] = relationship(
        'MusicsModel',
        secondary=music_artist_association,
        back_populates='artists',
        lazy='selectin',
        default_factory=list,
    )

    @property
    def musics_titles(self) -> List[str]:
        """Retorna dinamicamente apenas os títulos de todas as músicas deste artista."""
        return [music.title for music in self.musics]
