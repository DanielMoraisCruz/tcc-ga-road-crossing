from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import subqueryload, Session

from DataBase.database import create_table, Database
from GeneticAlgorithm.genetic_algorithm import GeneticAlgorithm
from Models.models import (
    ModelCitizen,
    ModelGeneration,
    ModelRoadCrossing,
    ModelSimulation,
)
from Models.response_models import ModelRoadCrossingResponse, ModelSimulationResponse, SimulationCreateResponse
from Models.schemas import (
    SchemaProcessResults,
    SchemaSimulation,
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




@app.post('/simulation/create', response_model=SimulationCreateResponse)
def create_simulation(simulation: SchemaSimulation, session: Session = Depends(Database.get_session)):
    try:

        simulation_db = Database.new_simulation_iteration(
            session,
            ModelSimulation(
                population=simulation.population,
                mutation_rate=simulation.mutationRate,
                selecteds=simulation.selecteds,
                avg_time_delta=simulation.avgTimeDelta,
                max_generations=simulation.maxGenerations,
                min_generations=simulation.minGenerations,
                mutation_method=simulation.mutationMethod,
            ),
        )

        return {'id': simulation_db.simulation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')


@app.post('/simulation/process-results/{simulation_id:int}', response_model=list[list[ModelRoadCrossingResponse]])
def process_results(simulation_id: int, results: list[SchemaProcessResults], session: Session = Depends(Database.get_session)):

    simulation = Database.get_simulation(session, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail='Simulação não encontrada')

    if simulation.population != len(results):
        raise HTTPException(status_code=500, detail=f'Resultados é maior que população registrada ao criar a simulação: ' f'deveria ser {simulation.population} mas é {len(results)}')

    generation = ModelGeneration(simulation_id=simulation.simulation_id)
    session.add(generation)
    session.flush()

    try:
        for citizen in results:
            saved_citizen = Database.save_results(
                session,
                ModelCitizen(
                    generation_id=generation.generation_id,
                    duration=citizen.simulatedTime,
                    trip_avg=citizen.avgTime,
                    occupation_rate=citizen.occupationRate,
                    vehicles_total=citizen.carsTotal,
                    average_speed=citizen.avgSpeed,
                ),
            )
            for light in citizen.lights:
                Database.new_road_crossing(
                    session,
                    ModelRoadCrossing(
                        citizen_id=saved_citizen.citizen_id,
                        red_duration=light.redDuration,
                        green_duration=light.greenDuration,
                        cycle_start_time=light.cycleStartTime,
                    ),
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao salvar resultados: {e}')

    try:
        # Executa crossover e mutação
        ga = GeneticAlgorithm(
            mutation_method=simulation.mutation_method,
            population=simulation.population,
            selecteds=simulation.selecteds,
            mutation_rate=simulation.mutation_rate,
        )

        # Critérios de parada
        print('Gerações na simulação: ', len(simulation.generations))
        if len(simulation.generations) >= simulation.min_generations:
            if ga.objective_function(simulation.avg_time_delta, simulation.generations):
                return []
        if len(simulation.generations) >= simulation.max_generations:
            return []

        new_population = ga.crossover(results)

        # Salva os resultados da simulação no banco de dados
        session.commit()
        print('Total de cidadãos:', len(new_population))
        return new_population

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao processar resultados: {e}')


@app.get('/simulation/final-results/{id}', response_model=ModelSimulationResponse)
def get_final_results(id: int, session: Session = Depends(Database.get_session)):
    try:
        result = (
            session.query(ModelSimulation)
            .options(
                # Start from ModelSimulation, and load generations
                subqueryload(ModelSimulation.generations)  # Load generations
                .subqueryload(ModelGeneration.citizens)  # Load citizens in each generation
                .subqueryload(ModelCitizen.road_crossings)
            )
            .filter_by(simulation_id=id)
            .first()
        )
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail='Resultados não encontrados')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar resultados: {e}')
    finally:
        session.close()


@app.get('/simulation/all', response_model=list[ModelSimulationResponse])
def get_all_simulations(session: Session = Depends(Database.get_session)) -> list[ModelSimulationResponse]:
    try:
        return session.query(ModelSimulation).order_by(ModelSimulation.simulation_id).all()  # Adaptar para o modelo de SchemaAll conforme necessário
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar todas simulações: {e}')
