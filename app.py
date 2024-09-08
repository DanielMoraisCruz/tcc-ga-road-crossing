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
    ModelCitizen,
    ModelRoadCrossing,
    ModelSimulation, ModelGeneration,
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
        simulation_db = db.new_simulation_iteration(
            session,
            ModelSimulation(
                selecteds=simulation.selecteds,
                mutation_rate=simulation.mutationRate,
                population=simulation.population,
                avg_time_delta=simulation.avgTimeDelta,
                max_generations=simulation.maxGenerations,
                min_generations=simulation.minGenerations,
            ),
        )

        return {'id': simulation_db.simulation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')


@app.post('/simulation/process-results/{id}')
def process_results(id: int, results: list[SchemaProcessResults], db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()

    simulation = db.get_simulation(session, id)

    if simulation.population != len(results):
        raise HTTPException(status_code=500, detail=f'Resultados é maior que população registrada ao criar '
                                                    f'a simulação: deveria ser {simulation.population} mas é {len(results)}')

    generation = ModelGeneration(simulation=simulation, simulation_id=simulation.simulation_id)


    try:
        # Salva os resultados da simulação no banco de dados
        db.create_new_generation(session, generation)

        for citizen in results:
            saved_citizen = db.save_results(
                session,
                ModelCitizen(
                    generation_id=generation.generation_id,
                    generation=generation,
                    duration=citizen.simulatedTime,
                    trip_avg=citizen.avgTime,
                    occupation_rate=citizen.occupationRate,
                    vehicles_total=citizen.carsTotal,
                    average_speed=citizen.avgSpeed,
                ),
            )
            for light in citizen.lights:
                db.new_road_crossing(
                    session,
                    ModelRoadCrossing(
                    citizen_id=saved_citizen.citizen_id,
                    red_duration=light.redDuration,
                    green_duration=light.greenDuration,
                    cycle_start_time=light.cycleStartTime,
                    citizen=saved_citizen,
                    )
                )


    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao salvar resultados: {e}')

    try:
        # Executa crossover e mutação

        ga = GeneticAlgorithm(
            population=simulation.population,
            selecteds=simulation.selecteds,
            mutation_rate=simulation.mutation_rate,
        )

        new_population = ga.crossover(results)

        if new_population is None:
            # TODO: Implementar status DONE
            return []


        # TODO: Colocar critério de paradas aqui

        return new_population

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao processar resultados: {e}')


@app.post('/simulation/done/{id}', response_model=SchemaDone)
def check_simulation_done(db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao verificar simulação: {e}')


@app.post('/simulation/premature-termination/{id}')
def premature_termination(id: int, db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        # Implementar lógica de término prematuro
        # Por exemplo, remover a simulação do banco de dados
        session.query(ModelSimulation).filter_by(simulationId=id).delete()
        session.commit()
        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao terminar simulação: {e}')


@app.get('/simulation/final-results/{id}', response_model=SchemaFinalResults)
def get_final_results(id: int, db: DatabaseInterface = Depends(get_database)):
    session = db.get_session()
    try:
        results = session.query(ModelSimulation).filter_by(simulationId=id).first()
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
        simulations = session.query(ModelSimulation).all()
        return simulations  # Adaptar para o modelo de SchemaAll conforme necessário
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar todas simulações: {e}')