import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# Helper function to convert snake_case to camelCase
def to_camel(string: str) -> str:
    components = string.split('_')
    camel_case = components[0] + ''.join(x.title() for x in components[1:])
    print(f"Converting {string} to {camel_case}")
    return camel_case


class ModelRoadCrossingResponse(BaseModel):
    road_crossing_id: Optional[int] = None  # Marked as Optional with default None
    red_duration: Optional[int] = None
    green_duration: Optional[int] = None
    cycle_start_time: Optional[int] = None
    created_at: Optional[datetime.datetime] = None  # Marked as Optional with default None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)


class ModelCitizenResponse(BaseModel):
    citizen_id: int
    duration: float
    trip_avg: float
    occupation_rate: float
    vehicles_total: int
    average_speed: float
    road_crossings: Optional[List[ModelRoadCrossingResponse]] = None  # Default to empty list
    created_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)


class ModelGenerationResponse(BaseModel):
    generation_id: int
    citizens: Optional[List[ModelCitizenResponse]] = None  # Default to empty list
    created_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)


class ModelSimulationResponse(BaseModel):
    simulation_id: int
    selecteds: int
    mutation_rate: float
    population: int
    avg_time_delta: float
    max_generations: int
    min_generations: int
    mutation_method: str
    generations: Optional[List[ModelGenerationResponse]] = None  # Default to empty list
    created_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)


class SimulationCreateResponse(BaseModel):
    id: int

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)
