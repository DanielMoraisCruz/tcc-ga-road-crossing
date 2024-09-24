from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class ModelSimulation:
    __tablename__ = 'SIMULATIONS'

    simulation_id: Mapped[Optional[int]] = mapped_column(primary_key=True, autoincrement=True, init=False)
    selecteds: Mapped[int] = mapped_column(Integer, nullable=False)
    mutation_rate: Mapped[float] = mapped_column(Float, nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_time_delta: Mapped[float] = mapped_column(Float, nullable=False)
    max_generations: Mapped[int] = mapped_column(Integer, nullable=False)
    min_generations: Mapped[int] = mapped_column(Integer, nullable=False)
    mutation_method: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    generations: Mapped[Optional[list['ModelGeneration']]] = relationship('ModelGeneration', lazy='select', init=False, default=[])


@table_registry.mapped_as_dataclass
class ModelGeneration:
    __tablename__ = 'GENERATIONS'

    generation_id: Mapped[Optional[int]] = mapped_column(primary_key=True, autoincrement=True, init=False)

    # Relacionamento com ModelSimulation
    simulation_id: Mapped[Optional[int]] = mapped_column(ForeignKey('SIMULATIONS.simulation_id'), nullable=True)

    citizens: Mapped[Optional[list['ModelCitizen']]] = relationship('ModelCitizen', lazy='subquery', init=False, default=[])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # simulation: Mapped[Optional['ModelSimulation']] = relationship('ModelSimulation', lazy='select')


@table_registry.mapped_as_dataclass
class ModelCitizen:
    __tablename__ = 'CITIZENS'

    citizen_id: Mapped[Optional[int]] = mapped_column(primary_key=True, autoincrement=True, init=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    trip_avg: Mapped[float] = mapped_column(Float, nullable=False)
    occupation_rate: Mapped[float] = mapped_column(Float, nullable=False)
    vehicles_total: Mapped[int] = mapped_column(Integer, nullable=False)
    average_speed: Mapped[float] = mapped_column(Float, nullable=False)

    generation_id: Mapped[Optional[int]] = mapped_column(ForeignKey('GENERATIONS.generation_id'), nullable=True)
    # generation: Mapped[Optional['ModelGeneration']] = relationship('ModelGeneration', lazy='select')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    road_crossings: Mapped[Optional[list['ModelRoadCrossing']]] = relationship('ModelRoadCrossing', lazy='subquery', init=False, default=[])


@table_registry.mapped_as_dataclass
class ModelRoadCrossing:
    __tablename__ = 'ROAD_CROSSING'

    red_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    green_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    cycle_start_time: Mapped[int] = mapped_column(Integer, nullable=False)

    citizen_id: Mapped[Optional[int]] = mapped_column(ForeignKey('CITIZENS.citizen_id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    road_crossing_id: Mapped[Optional[int]] = mapped_column(primary_key=True, autoincrement=True, init=False)

    # citizen: Mapped[Optional['ModelCitizen']] = relationship('ModelCitizen', lazy='select')
