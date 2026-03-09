import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

from table_templates import Product, GeneralProduct, Attributes, GeneralProductAttributes

# Load .env from the project root (one level above this file's directory)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
            port=os.getenv("POSTGRES_PORT")
        )
        self.cursor = self.connection.cursor()

    def test_connection(self) -> bool:
        try:
            self.cursor.execute("SELECT 1")
            result = self.cursor.fetchone()
            return result == (1,)
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def add_or_extract_general_product(self, general_product_data: GeneralProduct) -> int | None:
        try:
            # Trying insertion
            self.cursor.execute(
                """
                    INSERT INTO general_products(name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """,
                (general_product_data.get_sql_data()[1:])
            )
            result = self.cursor.fetchone()

            # Checking if insertion already exists
            if not result:
                self.cursor.execute(
                    "SELECT id FROM general_products WHERE name = %s",
                    (general_product_data.name,)
                )
                result = self.cursor.fetchone()

            self.connection.commit()
            return result[0]
        except Exception as e:
            self.connection.rollback()
            print(f"Database error: {e}")
            return None
    
    def add_or_extract_attribute(
        self,
        attribute: Attributes
    ) -> int | None:
        try:
            # Trying insertion
            self.cursor.execute(
                """
                    INSERT INTO attributes(name, unit, data_type)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name, unit, data_type) DO NOTHING
                    RETURNING id
                """,
                (attribute.get_sql_data()[1:])
            )
            result = self.cursor.fetchone()

            # Checking existance of the instance
            if not result:
                if attribute.unit is None:
                    self.cursor.execute(
                        "SELECT id FROM attributes WHERE name = %s AND unit IS NULL AND data_type = %s",
                        (attribute.name, attribute.data_type)
                    )
                else:
                    self.cursor.execute(
                        "SELECT id FROM attributes WHERE name = %s AND unit = %s AND data_type = %s",
                        (attribute.name, attribute.unit, attribute.data_type)
                    )
                result = self.cursor.fetchone()

            self.connection.commit()
            return result[0]
        except Exception as e:
            self.connection.rollback()
            print(f"Database error: {e}")
            return None
    
    def add_product(
        self,
        product: Product,
        general_product: GeneralProduct,
        attributes: list[Attributes],
        values: list[str],
        company_id: int,
        category_id: int
    ) -> bool:
        try:
            # Adding general product
            general_product_id = self.add_or_extract_general_product(general_product)
            if general_product_id is None:
                return False

            # Adding attributes
            for attribute, value in zip(attributes, values):
                attribute_id = self.add_or_extract_attribute(attribute)

                if attribute_id is None:
                    return False
                
                self.cursor.execute(
                    """
                        INSERT INTO general_product_attributes(value, attribute_id, general_product_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (attribute_id, general_product_id) DO NOTHING
                        RETURNING id
                    """,
                    (value, attribute_id, general_product_id)
                )

                # ON CONFLICT DO NOTHING returns nothing if the row already exists — that's fine
                if not self.cursor.fetchone():
                    self.cursor.execute(
                        "SELECT id FROM general_product_attributes WHERE attribute_id = %s AND general_product_id = %s",
                        (attribute_id, general_product_id)
                    )
                    if not self.cursor.fetchone():
                        return False

            # Tie corresponding data to the product
            product.general_product_id = general_product_id
            product.company_id = company_id
            product.category_id = category_id

            # Adding product
            self.cursor.execute(
                """
                    INSERT INTO products(buy_price, margin_percentage, general_product_id, company_id, category_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (general_product_id, company_id, category_id) DO NOTHING
                    RETURNING id
                """,
                (product.buy_price, product.margin_percentage, general_product_id, company_id, category_id)
            )

            if not self.cursor.fetchone():
                self.cursor.execute(
                    "SELECT id FROM products WHERE general_product_id = %s AND company_id = %s AND category_id = %s",
                    (general_product_id, company_id, category_id)
                )
                if not self.cursor.fetchone():
                    return False
            
            self.connection.commit() # commit
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Database connection error: {e}")
            return False