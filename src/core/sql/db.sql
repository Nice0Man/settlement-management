CREATE DATABASE settlement_management;

-- Подключение расширений
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- Таблица поселений
CREATE TABLE settlements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    climate_type VARCHAR(50) NOT NULL
);

-- Таблица инфраструктуры
CREATE TABLE infrastructure (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    settlement_id INTEGER REFERENCES settlements(id) ON DELETE CASCADE
);

-- Таблица ресурсов
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL,
    settlement_id INTEGER REFERENCES settlements(id) ON DELETE CASCADE
);

-- Создание таблицы операций с ресурсами (партиционирование по дате)
CREATE TABLE resource_operations (
    id SERIAL,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    settlement_id INTEGER REFERENCES settlements(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL DEFAULT now(),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    operation_type VARCHAR(20) NOT NULL CHECK (operation_type IN ('consumption', 'replenishment')),
    PRIMARY KEY (id, date)  -- Включаем date в PRIMARY KEY
) PARTITION BY RANGE (date);

-- Создание партиции для 2024 года
CREATE TABLE resource_operations_2024 PARTITION OF resource_operations
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Создание индекса для ускорения работы с датами
CREATE INDEX idx_resource_operations_date ON resource_operations (date);

-- Таблица персонала
CREATE TABLE personnel (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    infrastructure_id INTEGER REFERENCES infrastructure(id) ON DELETE SET NULL
);

-- Таблица датчиков и устройств
CREATE TABLE sensors_devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    infrastructure_id INTEGER REFERENCES infrastructure(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'inactive', 'faulty')),
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    energy_consumption INTEGER NOT NULL CHECK (energy_consumption >= 0)
);

-- Таблица событий
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT now(),
    event_type VARCHAR(50) NOT NULL,
    settlement_id INTEGER REFERENCES settlements(id) ON DELETE CASCADE
);

-- Таблица инцидентов
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    date_time TIMESTAMP NOT NULL DEFAULT now(),
    status VARCHAR(50) NOT NULL CHECK (status IN ('open', 'resolved', 'in_progress')),
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE
);

-- Таблица уведомлений
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT now(),
    status VARCHAR(50) NOT NULL CHECK (status IN ('unread', 'read'))
);

-- Таблица планов использования ресурсов
CREATE TABLE resource_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE
);

-- Таблица задач
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'overdue')),
    assignee VARCHAR(100) NOT NULL,
    deadline TIMESTAMP NOT NULL
);

-- Таблица геозон
CREATE TABLE geozones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    coordinates GEOMETRY(Point, 4326),
    description TEXT NOT NULL,
    usage_type VARCHAR(50) NOT NULL
);

-- Таблица маршрутов
CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    waypoints GEOMETRY(LineString, 4326),
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'inactive'))
);

-- Таблица энергетических систем
CREATE TABLE energy_systems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    current_load INTEGER NOT NULL CHECK (current_load >= 0),
    status VARCHAR(50) NOT NULL CHECK (status IN ('operational', 'offline', 'overloaded')),
    infrastructure_id INTEGER REFERENCES infrastructure(id) ON DELETE CASCADE
);

-- Таблица транспортных средств
CREATE TABLE transport_vehicles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('available', 'in_use', 'maintenance')),
    current_location GEOMETRY(Point, 4326),
    fuel_reserve INTEGER NOT NULL CHECK (fuel_reserve >= 0)
);

-- Таблица логистических маршрутов
CREATE TABLE logistic_routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    waypoints GEOMETRY(LineString, 4326),
    status VARCHAR(50) NOT NULL CHECK (status IN ('planned', 'active', 'completed'))
);


CREATE OR REPLACE FUNCTION check_resource_threshold() RETURNS TRIGGER AS $$
DECLARE
    current_level INTEGER;
    critical_threshold INTEGER := 50;  -- Условный критический порог
BEGIN
    -- Подсчет текущего количества ресурса
    SELECT COALESCE(SUM(quantity), 0) INTO current_level
    FROM resource_operations
    WHERE resource_id = NEW.resource_id;

    -- Если уровень ресурса ниже критического порога, создаем уведомление
    IF current_level < critical_threshold THEN
        INSERT INTO notifications (type, message, timestamp, status)
        VALUES ('warning', 'Критический уровень ресурса ID: ' || NEW.resource_id, now(), 'unread');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resource_threshold_trigger
AFTER INSERT ON resource_operations
FOR EACH ROW
EXECUTE FUNCTION check_resource_threshold();


CREATE OR REPLACE FUNCTION update_incident_status() RETURNS TRIGGER AS $$
BEGIN
    -- Если ресурс пополнен, обновляем статус инцидента
    UPDATE incidents
    SET status = 'resolved'
    WHERE resource_id = NEW.resource_id
    AND status = 'open';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER incident_status_update
AFTER INSERT ON resource_operations
FOR EACH ROW
WHEN (NEW.operation_type = 'replenishment')
EXECUTE FUNCTION update_incident_status();


CREATE OR REPLACE FUNCTION escalate_overdue_tasks() RETURNS TRIGGER AS $$
DECLARE
    senior_staff VARCHAR(100);
BEGIN
    -- Проверяем, истек ли срок выполнения задачи
    IF NEW.deadline < now() AND NEW.status = 'pending' THEN
        UPDATE tasks SET status = 'overdue' WHERE id = NEW.id;

        -- Определяем старшего персонала для эскалации задачи
        SELECT full_name INTO senior_staff FROM personnel
        WHERE position = 'Руководитель' LIMIT 1;

        INSERT INTO notifications (type, message, timestamp, status)
        VALUES ('alert', 'Задача "' || NEW.name || '" просрочена и передана ' || senior_staff, now(), 'unread');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER overdue_task_trigger
AFTER INSERT OR UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION escalate_overdue_tasks();


CREATE OR REPLACE FUNCTION redistribute_resources() RETURNS TRIGGER AS $$
DECLARE
    surplus_settlement_id INTEGER;
    available_quantity INTEGER;
BEGIN
    -- Ищем поселение с избыточным запасом данного ресурса
    SELECT settlement_id, SUM(quantity) INTO surplus_settlement_id, available_quantity
    FROM resource_operations
    WHERE resource_id = NEW.resource_id
    GROUP BY settlement_id
    HAVING SUM(quantity) > 100  -- Условный порог избыточного запаса
    LIMIT 1;

    -- Если есть избыточные запасы, выполняем перераспределение
    IF surplus_settlement_id IS NOT NULL THEN
        INSERT INTO resource_operations (resource_id, settlement_id, date, quantity, operation_type)
        VALUES (NEW.resource_id, surplus_settlement_id, now(), -50, 'consumption');

        INSERT INTO resource_operations (resource_id, settlement_id, date, quantity, operation_type)
        VALUES (NEW.resource_id, NEW.settlement_id, now(), 50, 'replenishment');

        INSERT INTO notifications (type, message, timestamp, status)
        VALUES ('info', 'Ресурс перераспределен между поселениями', now(), 'unread');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resource_redistribution_trigger
AFTER INSERT ON resource_operations
FOR EACH ROW
WHEN (NEW.quantity < 50 AND NEW.operation_type = 'consumption')
EXECUTE FUNCTION redistribute_resources();


CREATE OR REPLACE FUNCTION check_energy_consumption() RETURNS TRIGGER AS $$
DECLARE
    energy_limit INTEGER := 500;  -- Лимит потребления энергии
BEGIN
    -- Если текущее потребление превышает лимит, создаем уведомление
    IF NEW.energy_consumption > energy_limit THEN
        INSERT INTO notifications (type, message, timestamp, status)
        VALUES ('critical', 'Превышение потребления энергии устройством ID: ' || NEW.id, now(), 'unread');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER energy_consumption_trigger
AFTER INSERT OR UPDATE ON sensors_devices
FOR EACH ROW
EXECUTE FUNCTION check_energy_consumption();


CREATE OR REPLACE PROCEDURE replenish_resource(resource_id INTEGER, required_amount INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    available_stock INTEGER;
BEGIN
    -- Проверяем доступные запасы ресурса
    SELECT COALESCE(SUM(quantity), 0) INTO available_stock
    FROM resource_operations
    WHERE resource_id = replenish_resource.resource_id;

    -- Если ресурса достаточно, выполняем пополнение
    IF available_stock >= required_amount THEN
        INSERT INTO resource_operations (resource_id, settlement_id, date, quantity, operation_type)
        SELECT resource_id, settlement_id, now(), required_amount, 'replenishment'
        FROM resources WHERE id = resource_id;
    ELSE
        -- Создаем уведомление о нехватке ресурса
        INSERT INTO notifications (type, message, timestamp, status)
        VALUES ('warning', 'Нехватка ресурса ID: ' || resource_id, now(), 'unread');
    END IF;
END;
$$;
