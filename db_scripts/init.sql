CREATE TABLE IF NOT EXISTS companies(
    id SERIAL PRIMARY KEY,
    IIN VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) UNIQUE,
    owner VARCHAR(255),
    address VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS attributes(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50), -- cm, kg, NULL
    data_type VARCHAR(50) NOT NULL, -- number, text, boolean

    UNIQUE(name, unit, data_type)
);

CREATE TABLE IF NOT EXISTS general_products(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT Now(),
    updated_at TIMESTAMP DEFAULT Now()
);

CREATE TABLE IF NOT EXISTS general_product_attributes(
    id SERIAL PRIMARY KEY,
    value VARCHAR(255) NOT NULL,
    attribute_id INT NOT NULL,
    general_product_id INT NOT NULL,

    UNIQUE(attribute_id, general_product_id),

    FOREIGN KEY(attribute_id) REFERENCES attributes(id) ON DELETE CASCADE,
    FOREIGN KEY(general_product_id) REFERENCES general_products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categories(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    parent_id INT,

    FOREIGN KEY(parent_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS products(
    id SERIAL PRIMARY KEY,
    buy_price DECIMAL(10, 2) NOT NULL,
    margin_percentage DECIMAL(10, 2) DEFAULT 20.0,
    sell_price DECIMAL(10, 2),
    quantity INT DEFAULT 0,
    quality VARCHAR(255) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT Now(),
    updated_at TIMESTAMP DEFAULT Now(),
    general_product_id INT,
    company_id INT,
    category_id INT,

    FOREIGN KEY(general_product_id) REFERENCES general_products(id) ON DELETE SET NULL,
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS kaspi_products(
    id SERIAL PRIMARY KEY,
    kaspi_link VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL UNIQUE,
    kaspi_percentage DECIMAL(10, 2) DEFAULT 15.0,
    kaspi_minimal_price DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    product_id INT UNIQUE,

    FOREIGN KEY(product_id) REFERENCES products(id)
);

/* Creating functions */

CREATE OR REPLACE FUNCTION update_sell_price()
RETURNS TRIGGER AS $$
BEGIN
    NEW.sell_price := ROUND(NEW.buy_price * (1 + NEW.margin_percentage / 100), 2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;    

CREATE OR REPLACE FUNCTION update_minimal_kaspi_price()
RETURNS TRIGGER AS $$
DECLARE
    v_buy_price decimal(10, 2);
    v_margin_percent decimal(10, 2);
BEGIN
    SELECT buy_price, margin_percentage INTO v_buy_price, v_margin_percent FROM products WHERE id = NEW.product_id;
    NEW.kaspi_minimal_price := ROUND(
        v_buy_price * (1 + (v_margin_percent + NEW.kaspi_percentage) / 100), 2
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/* Creating triggers */

CREATE TRIGGER update_sell_price
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_sell_price();

CREATE TRIGGER update_minimal_kaspi_price
BEFORE INSERT OR UPDATE ON kaspi_products
FOR EACH ROW EXECUTE FUNCTION update_minimal_kaspi_price();

INSERT INTO categories(id, name, parent_id) VALUES(0, 'No category', NULL);
INSERT INTO companies(id, IIN, name, owner, address) VALUES(0, 'No company', 'No company', 'No company', 'No company');