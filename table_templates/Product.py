from dataclasses import dataclass

@dataclass
class Product:
    buy_price: float
    id: int = 0
    margin_percentage: float = 20.0
    quantity: int = 0
    quality: str = "Medium"
    general_product_id: int = 0
    category_id: int = 0
    company_id: int = 0

    def get_sql_data(self) -> tuple:
        return (
            self.id,
            self.buy_price,
            self.margin_percentage,
            self.quantity,
            self.quality,
            self.general_product_id,
            self.category_id,
            self.company_id
        )