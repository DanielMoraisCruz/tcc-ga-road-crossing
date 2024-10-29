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
    mutationMethod: str  # 'rim' ou 'pbm'


class SchemaReturnSimulation(BaseModel):
    id: int


class SchemaBaseRoadCrossing(BaseModel):
    redDuration: int
    greenDuration: int
    cycleStartTime: int


class SchemaProcessResults(BaseModel):
    avgTime: float
    carsTotal: int
    simulatedTime: float
    avgSpeed: float
    occupationRate: float
    lights: list[SchemaBaseRoadCrossing]
