import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    SchemaAll,
    SchemaDone,
    SchemaFinalResults,
    SchemaProcessResults,
    SchemaReturnSimulation,
    SchemaSimulation,
)
from SqlAlchemy.database import (
    DB_create_tables,
    DB_GetConfigAlgGen,
    DB_GetSession,
    DB_NewSimulationIteration,
    DB_SaveConfigAlgGen,
)
from SqlAlchemy.models import ModelConfigAlgGen, ModelRoadCrossing, ModelSimulationIteration
from sqlalchemy.orm import Session

app = FastAPI()

# Este método não atualiza tables já existentes
# Terá que usar uma migration tool (Alembic)
DB_create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost', 'http://localhost:8000', 'http://localhost:4200'],  # List the allowed origins
    allow_credentials=True,
    allow_methods=['*'],  # Allow all HTTP methods
    allow_headers=['*'],  # Allow all headers
)


@app.post('/simulation/create', response_model=SchemaReturnSimulation)
def createSimulation(simulation: SchemaSimulation, session: Session = Depends(DB_GetSession)):
    try:
        # Salva a configuração inicial da GA
        DB_SaveConfigAlgGen(
            session,
            config_algGen=ModelConfigAlgGen(
                population=simulation.population,
                mutation_rate=simulation.mutationRate,
                selecteds=simulation.selecteds,
            ),
        )
        session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')

    try:
        # Cria uma nova simulação no banco de dados

        simulationDB = DB_NewSimulationIteration(session,
            ModelSimulationIteration(
                selecteds=simulation.selecteds,
                mutation_rate=simulation.mutationRate,
                population=simulation.population
            )
        )
        return {'id': simulationDB.simulationId}  # Retorna o ID da simulação criada
    except Exception as e:
        print(e, __dict__)
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')


@app.post('/simulation/process-results/{id}')
def process_results(
    id: int, results: list[SchemaProcessResults], session: Session = Depends(DB_GetSession)
):
    try:
        all_lights: list = []
        for result in results:
            simulation_iteration = DB_NewSimulationIteration(
                session,
                ModelSimulationIteration(
                    duration=result.simulatedTime,
                    tripAvg=result.avgTime,
                    tripPeak=result.carsTotal,
                    densityPeak=result.occupationRate,
                    densityAvg=result.avgSpeed,
                    vehiclesTotal=result.carsTotal,
                    trafficLights=[
                        ModelRoadCrossing(
                            simulation_id=id,
                            redDuration=light['redDuration'],
                            greenDuration=light['greenDuration'],
                            cycleStartTime=light['cycleStartTime'],
                        )
                        for light in result.lights
                    ],
                ),
            )
            session.commit()
            # Adicionando os IDs dos semáforos em uma lista para cada iteração
            all_lights.append([light.simulation_id for light in simulation_iteration.roadCrossing])

        # Retornando a lista de listas de IDs dos semáforos
        return all_lights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao processar resultados: {e}')


@app.post('/simulation/done/{id}', response_model=SchemaDone)
def check_simulation_done(session: Session = Depends(DB_GetSession)):
    try:
        config = DB_GetConfigAlgGen(
            session,
        )
        done = config is None or config.population == 0  # Exemplo de verificação simples
        return {'done': done}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao verificar simulação: {e}')


@app.post('/simulation/premature-termination/{id}')
def premature_termination(id: int, session: Session = Depends(DB_GetSession)):
    try:
        # Implementar lógica de término prematuro
        # Por exemplo, remover a simulação do banco de dados
        session.query(ModelSimulationIteration).filter_by(simulationId=id).delete()
        session.commit()
        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao terminar simulação: {e}')


@app.get('/simulation/final-results/{id}', response_model=SchemaFinalResults)
def get_final_results(id: int, session: Session = Depends(DB_GetSession)):
    try:
        results = session.query(ModelSimulationIteration).filter_by(simulationId=id).first()
        if results:
            return results  # Adaptar para o modelo de SchemaFinalResults conforme necessário
        else:
            raise HTTPException(status_code=404, detail='Resultados não encontrados')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar resultados: {e}')


@app.get('/simulation/all', response_model=SchemaAll)
def get_all_simulations(session: Session = Depends(DB_GetSession)):
    try:
        simulations = session.query(ModelSimulationIteration).all()
        return simulations  # Adaptar para o modelo de SchemaAll conforme necessário
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar todas simulações: {e}')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
