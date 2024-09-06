from pydantic import BaseModel


class SchemaSimulation(BaseModel):
    """
    POST /simulation/create [Cria simulação]
        Back recebe objeto com simulatedTime,
        mutationRate, selecteds
        Front recebe id
    """

    population: int
    mutationRate: float
    selecteds: int
    minGenerations: int
    maxGenerations: int
    avgTimeDelta: float


class SchemaReturnSimulation(BaseModel):
    id: int


class SchemaBaseRoadCrossing(BaseModel):
    redDuration: int
    greenDuration: int
    cycleStartTime: int


class SchemaProcessResults(BaseModel):
    """
    POST /simulation/process-results/{id} [processa resultados da geração]
        Back recebe array de avgTime, carsTotal, simulatedTime, avgSpeed,
        occupationRate, lights[], iterateNext
        Front recebe lights[]
    """

    avgTime: float
    carsTotal: int
    simulatedTime: int
    avgSpeed: float
    occupationRate: float
    lights: list[SchemaBaseRoadCrossing]
    iterateNext: bool


class SchemaDone(BaseModel):
    """
    POST /simulation/done/{id} [retorna se simulação acabou ou não]
        Front recebe array com 1 item true ou false
    """

    done: bool


class SchemaPrematureTermination(BaseModel):
    """
    Ela add ao banco a informação de que aquela simulação acabou.
    POST /simulation/premature-termination/{id}
        Retorna status 200 se der certo
        qualquer erro retornar erro 5XX
    """

    pass


class SchemaFinalResults(BaseModel):
    """
    GET /simulation/final-results/{id} [retorna estatíticas]
        Front recebe resultados
    """

    pass


class SchemaAll(BaseModel):
    """
    GET /simulation/all
        Retorna lista de todas otimizações feitas
    """

    pass
