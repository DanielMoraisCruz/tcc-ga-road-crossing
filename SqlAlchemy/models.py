from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class ModelSimulationIteration:
    __tablename__ = 'ModelSimulationIteration'

    simulationId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    selecteds: Mapped[int] = mapped_column(Integer, nullable=False)
    mutation_rate: Mapped[float] = mapped_column(Float, nullable=False)


@table_registry.mapped_as_dataclass
class ModelRoadCrossing:
    __tablename__ = 'RoadCrossings'

    roadCrossingId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey('ModelSimulationIteration.simulationId'))
    redDuration: Mapped[int] = mapped_column(Integer, nullable=False)
    greenDuration: Mapped[int] = mapped_column(Integer, nullable=False)
    cycleStartTime: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relacionamento com ModelSimulationIteration
    simulation: Mapped['ModelSimulationIteration'] = relationship('ModelSimulationIteration')


@table_registry.mapped_as_dataclass
class ModelConfigAlgGen:
    __tablename__ = 'Config_AlgGen'

    configId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    num_selecteds: Mapped[int] = mapped_column(Integer, nullable=False)
    mutation_rate: Mapped[float] = mapped_column(Float, nullable=False)
