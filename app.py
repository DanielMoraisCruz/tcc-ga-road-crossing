import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from genetic_algorithm import GeneticAlgorithm
from schemas import (
    SchemaAll,
    SchemaDone,
    SchemaFinalResults,
    SchemaProcessResults,
    SchemaReturnSimulation,
    SchemaSimulation,
)
from SqlAlchemy.database import Database, create_table, engine
from SqlAlchemy.database_interface import DatabaseInterface
from SqlAlchemy.models import (
    ModelConfigAlgGen,
    ModelResults,
    ModelRoadCrossing,
    ModelSimulationIteration,
)

app = FastAPI()

# Este método não atualiza tables já existentes
# Terá que usar uma migration tool (Alembic)
create_table()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[  # List the allowed origins
        'http://localhost',
        'http://localhost:8000',
        'http://localhost:4200',
    ],
    allow_credentials=True,
    allow_methods=['*'],  # Allow all HTTP methods
    allow_headers=['*'],  # Allow all headers
)


def get_database() -> DatabaseInterface:
    return Database(engine)


@app.post('/simulation/create', response_model=SchemaReturnSimulation)
def create_simulation(simulation: SchemaSimulation, db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        db.save_config_alg_gen(
            session,
            ModelConfigAlgGen(
                population=simulation.population,
                mutation_rate=simulation.mutationRate,
                selecteds=simulation.selecteds,
            ),
        )
        simulation_db = db.new_simulation_iteration(
            session,
            ModelSimulationIteration(
                selecteds=simulation.selecteds,
                mutation_rate=simulation.mutationRate,
                population=simulation.population,
            ),
        )
        # for light in simulation.lights:
        #     db.new_road_crossing(
        #         session,
        #         ModelRoadCrossing(
        #             simulation_id=simulation_db.simulationId,
        #             redDuration=light.redDuration,
        #             greenDuration=light.greenDuration,
        #             cycleStartTime=light.cycleStartTime,
        #         ),
        #     )
        return {'id': simulation_db.simulationId}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')


@app.post('/simulation/process-results/{id}')
def process_results(id: int, results: list[SchemaProcessResults], db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        # Salva os resultados da simulação no banco de dados
        for result in results:
            db.save_results(
                session,
                ModelResults(
                    simulation_id=id,
                    duration=result.avgTime,
                    tripAvg=result.avgSpeed,
                    tripPeak=result.carsTotal,
                    vehiclesTotal=result.carsTotal,
                    occupationRate=result.occupationRate,
                ),
            )
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao salvar resultados: {e}')

    try:
        # Executa crossover e mutação
        config = db.get_config_alg_gen(
            session,
            id_simulation=id,
        )
        if config is None:
            raise HTTPException(status_code=404, detail='Configuração não encontrada')

        ga = GeneticAlgorithm(
            population=config.population,
            selecteds=config.selecteds,
            mutation_rate=config.mutation_rate,
        )

        parents = db.get_road_crossings(session, id)
        new_population = ga.crossover(parents)
        if new_population is None:
            return 0

        db.save_config_alg_gen(
            session,
            ModelConfigAlgGen(
                population=new_population,
                selecteds=config.selecteds,
                mutation_rate=config.mutation_rate,
            ),
        )

        # Salva os novos semaforos
        for light in new_population:
            db.new_road_crossing(
                session,
                ModelRoadCrossing(
                    simulation_id=id,
                    redDuration=light.redDuration,
                    greenDuration=light.greenDuration,
                    cycleStartTime=light.cycleStartTime,
                ),
            )
        # Pega e retorna todos os semaforos sem seus ids
        return db.get_road_crossing_no_id(session, id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao processar resultados: {e}')


@app.post('/simulation/done/{id}', response_model=SchemaDone)
def check_simulation_done(db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        config = db.get_config_alg_gen(session, id_simulation=id)
        # Todo: Implementar lógica para verificar se a simulação acabou
        done = config is None or config.population == 0  # Exemplo de verificação simples
        return {'done': done}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao verificar simulação: {e}')


@app.post('/simulation/premature-termination/{id}')
def premature_termination(id: int, db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        # Implementar lógica de término prematuro
        # Por exemplo, remover a simulação do banco de dados
        session.query(ModelSimulationIteration).filter_by(simulationId=id).delete()
        session.commit()
        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao terminar simulação: {e}')


@app.get('/simulation/final-results/{id}', response_model=SchemaFinalResults)
def get_final_results(id: int, db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        results = session.query(ModelSimulationIteration).filter_by(simulationId=id).first()
        if results:
            return results  # Adaptar para o modelo de SchemaFinalResults conforme necessário
        else:
            raise HTTPException(status_code=404, detail='Resultados não encontrados')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar resultados: {e}')


@app.get('/simulation/all', response_model=SchemaAll)
def get_all_simulations(db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        simulations = session.query(ModelSimulationIteration).all()
        return simulations  # Adaptar para o modelo de SchemaAll conforme necessário
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar todas simulações: {e}')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
