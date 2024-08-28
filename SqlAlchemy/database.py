from settings import Settings
from SqlAlchemy import loggings
from sqlalchemy import create_engine
from SqlAlchemy.models import ModelConfigAlgGen, ModelRoadCrossing, ModelSimulationIteration
from sqlalchemy.orm import Session

engine = create_engine(Settings().DATABASE_URL)
log = loggings.Log('database')


def DB_GetSession() -> Session:
    with Session(engine) as session:
        yield session


def DB_NewRoadCrossing(session: Session, road_crossing: ModelRoadCrossing):
    try:
        session.add(road_crossing)
    except Exception as e:
        log.log_error(f'Erro ao criar o cruzamento: {e}')
        session.rollback()
        raise


def DB_NewSimulationIteration(session: Session, simulation_iteration: ModelSimulationIteration):
    try:
        session.add(simulation_iteration)
        session.commit()
        return simulation_iteration
    except Exception as e:
        log.log_error(f'Erro ao criar simulação: {e}')
        session.rollback()
        raise


def DB_GetSimulationIteration(session: Session, id_simulation: int) -> ModelSimulationIteration:
    try:
        simulation = (
            session.query(ModelSimulationIteration)
            .filter(ModelSimulationIteration.simulationId == id_simulation)
            .first()
        )
        return simulation
    except Exception as e:
        log.log_error(f'Erro ao buscar simulação: {e}')
        session.rollback()
        raise


def DB_SaveConfigAlgGen(session: Session, config_algGen: ModelConfigAlgGen):
    try:
        session.add(config_algGen)
        session.commit()
        return config_algGen
    except Exception as e:
        log.log_error(f'Erro ao salvar configuração AlgGen: {e}')
        session.rollback()
        raise


# retorna a configuração do algoritmo genético com o ID correspondente
def DB_GetConfigAlgGen(session: Session, id_simulation: int) -> ModelConfigAlgGen:
    try:
        config = (
            session.query(ModelConfigAlgGen)
            .filter(ModelConfigAlgGen.configId == id_simulation)
            .first()
        )
        return config
    except Exception as e:
        log.log_error(f'Erro ao buscar configuração AlgGen: {e}')
        session.rollback()
        raise


def DB_PatchConfigAlgGen(
    session: Session,
    new_population: list[dict[str, int]] = [{'null': 0}],
    num_selecteds: int = 0,
    mutation_rate: float = 0.0,
) -> ModelConfigAlgGen:
    try:
        config = session.query(ModelConfigAlgGen).first()
        if config:
            config.population = new_population if new_population[0]['null'] else config.population
            config.selecteds = num_selecteds if num_selecteds != 0 else config.selecteds
            config.mutation_rate = mutation_rate if mutation_rate != 0.0 else config.mutation_rate
            session.commit()
            return config
        else:
            log.log_warning('Config AlgGen não encontrada para atualizar')
            return None
    except Exception as e:
        log.log_error(f'Erro ao atualizar configuração AlgGen: {e}')
        session.rollback()
        raise
