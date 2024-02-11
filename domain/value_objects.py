from pydantic import BaseModel


class IRRCurrency(BaseModel):
    value: str = 'IRR'