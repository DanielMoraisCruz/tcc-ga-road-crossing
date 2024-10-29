from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from DataBase.database_interface import DatabaseInterface
from Models.models import (
    ModelCitizen,
    ModelGeneration,
    ModelRoadCrossing,
    ModelSimulation,
    table_registry,
)
from settings import Settings

engine = create_engine(Settings().DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_table() -> None:
    # drop_table()
    table_registry.metadata.create_all(bind=engine)
    print('Banco de dados criado com sucesso.')


class Database(DatabaseInterface):
    def __init__(self, _engine):
        self.engine = _engine

    @staticmethod
    def get_session() -> Session:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def new_simulation_iteration(session: Session, simulation_iteration: ModelSimulation) -> ModelSimulation:
        session.add(simulation_iteration)
        session.commit()
        return simulation_iteration

    @staticmethod
    def new_road_crossing(session: Session, road_crossing: ModelRoadCrossing) -> ModelRoadCrossing:
        session.add(road_crossing)
        session.commit()
        return road_crossing

    @staticmethod
    def save_results(session: Session, results: ModelCitizen) -> ModelCitizen:
        session.add(results)
        session.commit()
        return results

    @staticmethod
    def get_results(session: Session, id_simulation: int) -> list:
        return session.query(ModelCitizen).filter(ModelCitizen.simulation_id == id_simulation).all()

    @staticmethod
    def get_road_crossings(session: Session, id_simulation: int) -> list:
        return session.query(ModelRoadCrossing).filter(ModelRoadCrossing.simulation_id == id_simulation).all()

    @staticmethod
    def get_simulation(session: Session, id_simulation: int) -> Optional[ModelSimulation]:
        return session.query(ModelSimulation).filter(ModelSimulation.simulation_id == id_simulation).first()

    @staticmethod
    def delete_road_crossing(session: Session, id_simulation: int) -> None:
        session.query(ModelRoadCrossing).filter(ModelRoadCrossing.simulation_id == id_simulation).delete()
        session.commit()

    @staticmethod
    def create_new_generation(session: Session, generation: ModelGeneration):
        session.add(generation)
        session.commit()
        return generation
