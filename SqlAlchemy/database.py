# database.py
from typing import List, Optional

from database_interface import DatabaseInterface

from SqlAlchemy.models import (
    ModelConfigAlgGen,
    ModelResults,
    ModelRoadCrossing,
    ModelSimulationIteration,
    table_registry,
)
from sqlalchemy.orm import Session


class Database(DatabaseInterface):
    def __init__(self, engine):
        self.engine = engine

    def create_tables(self) -> None:
        table_registry.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return Session(self.engine)

    @staticmethod
    def new_road_crossing(session: Session, road_crossing: ModelRoadCrossing) -> None:
        session.add(road_crossing)
        session.commit()

    @staticmethod
    def new_simulation_iteration(
        session: Session, simulation_iteration: ModelSimulationIteration
    ) -> ModelSimulationIteration:
        session.add(simulation_iteration)
        session.commit()
        return simulation_iteration

    @staticmethod
    def get_simulation_iteration(
        session: Session, id_simulation: int
    ) -> Optional[ModelSimulationIteration]:
        return (
            session.query(ModelSimulationIteration)
            .filter(ModelSimulationIteration.simulationId == id_simulation)
            .first()
        )

    @staticmethod
    def save_config_alg_gen(
        session: Session, config_alg_gen: ModelConfigAlgGen
    ) -> ModelConfigAlgGen:
        session.add(config_alg_gen)
        session.commit()
        return config_alg_gen

    @staticmethod
    def get_config_alg_gen(session: Session, id_simulation: int) -> Optional[ModelConfigAlgGen]:
        return (
            session.query(ModelConfigAlgGen)
            .filter(ModelConfigAlgGen.configId == id_simulation)
            .first()
        )

    @staticmethod
    def save_results(session: Session, results: ModelResults) -> None:
        session.add(results)
        session.commit()

    @staticmethod
    def get_results(session: Session, id_simulation: int) -> List[ModelResults]:
        return session.query(ModelResults).filter(ModelResults.simulation_id == id_simulation).all()

    @staticmethod
    def get_road_crossings(session: Session, id_simulation: int) -> List[ModelRoadCrossing]:
        return (
            session.query(ModelRoadCrossing)
            .filter(ModelRoadCrossing.simulation_id == id_simulation)
            .all()
        )

    @staticmethod
    def get_road_crossing_no_id(session: Session, id_simulation: int) -> List[ModelRoadCrossing]:
        return (
            session.query(ModelRoadCrossing)
            .filter(ModelRoadCrossing.simulation_id == id_simulation)
            .with_entities(
                ModelRoadCrossing.redDuration,
                ModelRoadCrossing.greenDuration,
                ModelRoadCrossing.cycleStartTime,
            )
            .all()
        )

    @staticmethod
    def get_simulation(session: Session, id_simulation: int) -> Optional[ModelSimulationIteration]:
        return (
            session.query(ModelSimulationIteration)
            .filter(ModelSimulationIteration.simulationId == id_simulation)
            .first()
        )
