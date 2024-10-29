from typing import List, Optional

from sqlalchemy.orm import Session

from Models.models import (
    ModelCitizen,
    ModelGeneration,
    ModelRoadCrossing,
    ModelSimulation,
)


class DatabaseInterface:
    @staticmethod
    def get_session() -> Session:
        raise NotImplementedError

    @staticmethod
    def new_simulation_iteration(session: Session, simulation_iteration: ModelSimulation) -> ModelSimulation:
        raise NotImplementedError

    @staticmethod
    def new_road_crossing(session: Session, road_crossing: ModelRoadCrossing) -> ModelRoadCrossing:
        raise NotImplementedError

    @staticmethod
    def save_results(session: Session, results: ModelCitizen) -> ModelCitizen:
        raise NotImplementedError

    @staticmethod
    def get_results(session: Session, id_simulation: int) -> List[ModelCitizen]:
        raise NotImplementedError

    @staticmethod
    def get_road_crossings(session: Session, id_simulation: int) -> List[ModelRoadCrossing]:
        raise NotImplementedError

    @staticmethod
    def get_road_crossing_no_id(session: Session, id_simulation: int) -> List[ModelRoadCrossing]:
        raise NotImplementedError

    @staticmethod
    def get_simulation(session: Session, id_simulation: int) -> Optional[ModelSimulation]:
        raise NotImplementedError

    @staticmethod
    def delete_road_crossing(session: Session, id_simulation: int) -> None:
        raise NotImplementedError

    @staticmethod
    def create_new_generation(session: Session, generation: ModelGeneration) -> ModelGeneration:
        raise NotImplementedError
