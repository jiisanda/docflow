from pydantic import BaseModel

class SharingRequest(BaseModel):
    visits: int = 1     # default value of visits (1)
