from pydantic import BaseModel


class VolumePrior(BaseModel):
    slug: str
    mean: float
    support: int
    alpha: float
    beta: float
