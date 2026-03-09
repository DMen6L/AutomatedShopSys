from database import Database
from table_templates import Product, GeneralProduct, Attributes

def ok(label: str, value):
    print(f"  ✓  {label}: {value}")
    return value

def fail(label: str, value=None):
    print(f"  ✗  {label}: {value!r}")

def test_connection(db: Database):
    print("\n[1] Connection test")
    if db.test_connection():
        ok("Connected to database", True)
    else:
        fail("Could not connect to database")

def test_add_general_product(db: Database) -> int | None:
    print("\n[2] add_general_product")
    gp = GeneralProduct(id=0, name="Test Laptop", description="A generic test laptop")
    gp_id = db.add_general_product(gp)
    if gp_id:
        ok("Inserted / found general_product id", gp_id)
    else:
        fail("add_general_product returned None")
    return gp_id

def test_add_attribute(db: Database) -> int | None:
    print("\n[3] add_attribute")
    attr = Attributes(id=0, name="RAM", unit="GB", data_type="number")
    attr_id = db.add_attribute(attr)
    if attr_id:
        ok("Inserted / found attribute id", attr_id)
    else:
        fail("add_attribute returned None")
    return attr_id

def test_add_product(db: Database):
    print("\n[4] add_product  (end-to-end)")

    general_product = GeneralProduct(id=0, name="Test Monitor", description="27-inch IPS")
    attributes      = [
        Attributes(id=0, name="Screen Size", unit="inch", data_type="number"),
        Attributes(id=0, name="Resolution",  unit=None,   data_type="text"),
    ]
    values          = ["27", "2560x1440"]
    product         = Product(id=0, buy_price=250.00, margin_percentage=20.0)

    success = db.add_product(
        product=product,
        general_product=general_product,
        attributes=attributes,
        values=values,
        company_id=product.company_id,
        category_id=product.category_id
    )

    if success:
        ok("add_product succeeded", True)
    else:
        fail("add_product returned False — check company_id/category_id exist in DB")

def main():
    print("=" * 50)
    print("  Database integration test")
    print("=" * 50)

    db = Database()

    test_connection(db)
    test_add_general_product(db)
    test_add_attribute(db)
    test_add_product(db)

    print("\n" + "=" * 50)
    print("  Done.")
    print("=" * 50)

if __name__ == "__main__":
    main()