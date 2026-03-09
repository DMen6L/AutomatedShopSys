from dataclasses import dataclass

@dataclass
class GeneralProductAttributes:
    value: str
    attribute_id: int
    general_product_id: int
    id: int = 0

    def get_sql_data(self) -> tuple:
        return (
            self.id,
            self.value,
            self.attribute_id,
            self.general_product_id
        )