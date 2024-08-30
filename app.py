from fastapi import Depends, FastAPI, HTTPException

from schemas import (
    SchimaAll,
    SchimaDone,
    SchimaFinalResults,
    SchimaProcessResults,
    SchimaReturnSimulation,
    SchimaSimulation,
)
from SqlAlchemy.database import (
    DB_GetConfigAlgGen,
    DB_GetSession,
    DB_NewSimulationIteration,
    DB_SaveConfigAlgGen,
)
from SqlAlchemy.models import ModelConfigAlgGen, ModelRoadCrossing, ModelSimulationIteration
from sqlalchemy.orm import Session

app = FastAPI()


@app.post('/simulation/create', response_model=SchimaReturnSimulation)
def createSimulation(simulation: SchimaSimulation, session: Session = Depends(DB_GetSession)):
    try:
        # Salva a configuração inicial da GA
        DB_SaveConfigAlgGen(
            session,
            config_algGen=ModelConfigAlgGen(
                population=simulation.population,
                generations=simulation.generations,
                selecteds=simulation.selecteds,
            ),
        )
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')

    try:
        # Cria uma nova simulação no banco de dados
        simulationDB = (
            session,
            ModelSimulationIteration(
                selecteds=simulation.selecteds,
                mutation_rate=simulation.mutationRate,
            ),
        )

        return {'id': simulationDB.simulationId}  # Retorna o ID da simulação criada
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao criar simulação: {e}')


@app.post('/simulation/process-results/{id}')
def process_results(
    id: int, results: list[SchimaProcessResults], session: Session = Depends(DB_GetSession)
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


@app.post('/simulation/done/{id}', response_model=SchimaDone)
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


@app.get('/simulation/final-results/{id}', response_model=SchimaFinalResults)
def get_final_results(id: int, session: Session = Depends(DB_GetSession)):
    try:
        results = session.query(ModelSimulationIteration).filter_by(simulationId=id).first()
        if results:
            return results  # Adaptar para o modelo de SchimaFinalResults conforme necessário
        else:
            raise HTTPException(status_code=404, detail='Resultados não encontrados')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar resultados: {e}')


@app.get('/simulation/all', response_model=SchimaAll)
def get_all_simulations(session: Session = Depends(DB_GetSession)):
    try:
        simulations = session.query(ModelSimulationIteration).all()
        return simulations  # Adaptar para o modelo de SchimaAll conforme necessário
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro ao buscar todas simulações: {e}')
