CREATE TABLE Items (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255)
);

CREATE TABLE HourlyPrices (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES Items(item_id),
    timestamp TIMESTAMP NOT NULL,
    price INT NOT NULL,
    volume INT
);
