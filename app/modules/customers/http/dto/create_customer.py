from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CreateCustomerDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_name: str = Field(alias="cliente_nome")
    customer_email: EmailStr = Field(alias="cliente_email")
    solicitation_type: str = Field(alias="tipo_solicitacao")
    patrimony_value: float = Field(alias="valor_patrimonio")
