CREATE TABLE IF NOT EXISTS customers (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id)
        ON DELETE CASCADE,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    registration_number VARCHAR(30) UNIQUE NOT NULL,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS services (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    duration_minutes INTEGER NOT NULL DEFAULT 60
        CHECK (duration_minutes > 0)
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
    service_id INTEGER NOT NULL REFERENCES services(id),
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'scheduled'
        CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    appointment_id INTEGER NOT NULL REFERENCES appointments(id)
        ON DELETE CASCADE,
    description TEXT NOT NULL,
    cost NUMERIC(10, 2) NOT NULL DEFAULT 0
        CHECK (cost >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed')),
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id)
        ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
