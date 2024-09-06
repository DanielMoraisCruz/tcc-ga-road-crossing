from typing import List, Optional

from SqlAlchemy.models import (
    ModelConfigAlgGen,
    ModelResults,
    ModelRoadCrossing,
    ModelSimulationIteration,
)
from sqlalchemy.orm import Session


class DatabaseInterface:
    def create_table(self) -> None:
        raise NotImplementedError

    def get_session(self) -> Session:
        raise NotImplementedError

    @staticmethod
    def save_config_alg_gen(session: Session, config_alg_gen: ModelConfigAlgGen) -> ModelConfigAlgGen:
        raise NotImplementedError

    @staticmethod
    def new_simulation_iteration(session: Session, simulation_iteration: ModelSimulationIteration) -> ModelSimulationIteration:
        raise NotImplementedError

    @staticmethod
    def new_road_crossing(session: Session, road_crossing: ModelRoadCrossing) -> ModelRoadCrossing:
        raise NotImplementedError

    @staticmethod
    def get_simulation_iteration(session: Session, id_simulation: int) -> Optional[ModelSimulationIteration]:
        raise NotImplementedError

    @staticmethod
    def get_config_alg_gen(session: Session, id_simulation: int) -> Optional[ModelConfigAlgGen]:
        raise NotImplementedError

    @staticmethod
    def save_results(session: Session, results: ModelResults) -> None:
        raise NotImplementedError

    @staticmethod
    def get_results(session: Session, id_simulation: int) -> List[ModelResults]:
        raise NotImplementedError

    @staticmethod
    def get_road_crossings(session: Session, id_simulation: int) -> List[ModelRoadCrossing]:
        raise NotImplementedError

    @staticmethod
    def get_road_crossing_no_id(session: Session, id_simulation: int) -> List[ModelRoadCrossing]:
        raise NotImplementedError

    @staticmethod
    def get_simulation(session: Session, id_simulation: int) -> Optional[ModelSimulationIteration]:
        raise NotImplementedError
