from abc import ABC, abstractmethod

class ICustomerRepository(ABC):
    @abstractmethod
    def create_customer(self, customer_data):
        pass

    @abstractmethod
    def get_customer_by_id(self, customer_id):
        pass

    @abstractmethod
    def get_customer_by_email(self, email):
        pass

    @abstractmethod
    def update_customer(self, customer_id, updated_data):
        pass

    @abstractmethod
    def delete_customer(self, customer_id):
        pass