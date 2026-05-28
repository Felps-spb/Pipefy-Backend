

class CustomerAlreadyExistsException(Exception):
    def __init__(self, email: str):
        super().__init__(f"Cliente com email {email} já existe")


class CustomerNotFoundException(Exception):
    def __init__(self, email: str):
        super().__init__(f"Cliente com email {email} não encontrado")