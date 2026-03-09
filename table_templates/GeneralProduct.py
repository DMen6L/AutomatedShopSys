from dataclasses import dataclass

@dataclass
class GeneralProduct:
    name: str
    description: str = ""
    id: int = 0
    
    def get_sql_data(self) -> tuple:
        return (
            self.id,
            self.name,
            self.description
        )