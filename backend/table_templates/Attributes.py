from dataclasses import dataclass

@dataclass
class Attributes:
    name: str
    unit: str | None
    data_type: str
    id: int = 0

    def get_sql_data(self) -> tuple:
        return (
            self.id,
            self.name,
            self.unit,
            self.data_type
        )