from pydantic import BaseModel


class SchimaSimulation(BaseModel):
    """
    POST /simulation/create [Cria simulação]
        Back recebe objeto com simulatedTime,
        mutationRate, selecteds
        Front recebe id
    """

    simulatedTime: int
    mutationRate: float
    selecteds: int


class SchimaReturnSimulation(BaseModel):
    id: int


class SchimaBaseRoadCrossing(BaseModel):
    redDuration: int
    greenDuration: int
    cycleStartTime: int


class SchimaProcessResults(BaseModel):
    """
    POST /simulation/process-results/{id} [processa resultados da geração]
        Back recebe array de avgTime, carsTotal, simulatedTime, avgSpeed,
        occupationRate, lights[], iterateNext
        Front recebe lights[]
    """

    avgTime: int
    carsTotal: int
    simulatedTime: int
    avgSpeed: int
    occupationRate: int
    lights: list[SchimaBaseRoadCrossing]
    iterateNext: bool


class SchimaDone(BaseModel):
    """
    POST /simulation/done/{id} [retorna se simulação acabou ou não]
        Front recebe array com 1 item true ou false
    """

    done: bool


class SchimaPrematureTermination(BaseModel):
    """
    Ela add ao banco a informação de que aquela simulação acabou.
    POST /simulation/premature-termination/{id}
        Retorna status 200 se der certo
        qualquer erro retornar erro 5XX
    """

    pass


class SchimaFinalResults(BaseModel):
    """
    GET /simulation/final-results/{id} [retorna estatíticas]
        Front recebe resultados
    """

    pass


class SchimaAll(BaseModel):
    """
    GET /simulation/all
        Retorna lista de todas otimizações feitas
    """

    pass
