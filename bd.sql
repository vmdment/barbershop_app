-- ============================================================
-- DATABASE CREATION SCRIPT: BARBERSHOP (15 TABLES)
-- SINGULAR ENTITIES & ENGLISH ATTRIBUTES
-- ============================================================

CREATE DATABASE IF NOT EXISTS barbershop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE barbershop_db;

-- 1. Role
CREATE TABLE IF NOT EXISTS role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 2. User
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 3. Barbershop (Location / Shop)
CREATE TABLE IF NOT EXISTS barbershop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manager_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(150) NOT NULL,
    city VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    CONSTRAINT fk_barbershop_user FOREIGN KEY (manager_id) REFERENCES user(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 4. Barber
CREATE TABLE IF NOT EXISTS barber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    barbershop_id INT NULL,
    provides_home_service TINYINT(1) DEFAULT 0,
    provides_shop_service TINYINT(1) DEFAULT 1,
    commission_rate DECIMAL(5,2) DEFAULT 0.00,
    is_active TINYINT(1) DEFAULT 1,
    CONSTRAINT fk_barber_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_barber_barbershop FOREIGN KEY (barbershop_id) REFERENCES barbershop(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5. Barber Schedule
CREATE TABLE IF NOT EXISTS barber_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barber_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    lunch_start_time TIME NULL,
    lunch_end_time TIME NULL,
    CONSTRAINT fk_schedule_barber FOREIGN KEY (barber_id) REFERENCES barber(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Schedule Block
CREATE TABLE IF NOT EXISTS schedule_block (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barber_id INT NOT NULL,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    reason VARCHAR(255) NULL,
    CONSTRAINT fk_block_barber FOREIGN KEY (barber_id) REFERENCES barber(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Service
CREATE TABLE IF NOT EXISTS service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    duration_minutes INT NOT NULL,
    buffer_minutes INT DEFAULT 10,
    CONSTRAINT chk_duration CHECK (duration_minutes > 0)
) ENGINE=InnoDB;

-- 8. Barber Service (Junction Table)
CREATE TABLE IF NOT EXISTS barber_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barber_id INT NOT NULL,
    service_id INT NOT NULL,
    custom_price DECIMAL(10,2) NULL,
    custom_duration_minutes INT NULL,
    CONSTRAINT fk_bs_barber FOREIGN KEY (barber_id) REFERENCES barber(id) ON DELETE CASCADE,
    CONSTRAINT fk_bs_service FOREIGN KEY (service_id) REFERENCES service(id) ON DELETE CASCADE,
    CONSTRAINT uk_barber_service UNIQUE(barber_id, service_id)
) ENGINE=InnoDB;

-- 9. Appointment (Booking / Reservation)
CREATE TABLE IF NOT EXISTS appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    barber_id INT NOT NULL,
    barbershop_id INT NULL,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location_type ENUM('Shop', 'Home') NOT NULL,
    home_address VARCHAR(200) NULL,
    status ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Pending',
    total_amount DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_appointment_customer FOREIGN KEY (customer_id) REFERENCES user(id) ON DELETE RESTRICT,
    CONSTRAINT fk_appointment_barber FOREIGN KEY (barber_id) REFERENCES barber(id) ON DELETE RESTRICT,
    CONSTRAINT fk_appointment_barbershop FOREIGN KEY (barbershop_id) REFERENCES barbershop(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 10. Appointment Service Detail
CREATE TABLE IF NOT EXISTS appointment_service_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    service_id INT NOT NULL,
    applied_price DECIMAL(10,2) NOT NULL,
    applied_duration_minutes INT NOT NULL,
    CONSTRAINT fk_asd_appointment FOREIGN KEY (appointment_id) REFERENCES appointment(id) ON DELETE CASCADE,
    CONSTRAINT fk_asd_service FOREIGN KEY (service_id) REFERENCES service(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 11. Product
CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barbershop_id INT NULL,
    barber_id INT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    min_stock_level INT DEFAULT 5,
    CONSTRAINT fk_product_barbershop FOREIGN KEY (barbershop_id) REFERENCES barbershop(id) ON DELETE CASCADE,
    CONSTRAINT fk_product_barber FOREIGN KEY (barber_id) REFERENCES barber(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. Product Sale
CREATE TABLE IF NOT EXISTS product_sale (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NULL,
    seller_user_id INT NOT NULL,
    sale_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('Cash', 'Card', 'Transfer') NOT NULL,
    CONSTRAINT fk_ps_customer FOREIGN KEY (customer_id) REFERENCES user(id) ON DELETE SET NULL,
    CONSTRAINT fk_ps_seller FOREIGN KEY (seller_user_id) REFERENCES user(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 13. Product Sale Detail
CREATE TABLE IF NOT EXISTS product_sale_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_psd_sale FOREIGN KEY (product_sale_id) REFERENCES product_sale(id) ON DELETE CASCADE,
    CONSTRAINT fk_psd_product FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 14. Supplier
CREATE TABLE IF NOT EXISTS supplier (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100) NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NULL,
    address VARCHAR(150) NULL
) ENGINE=InnoDB;

-- 15. Supplier Purchase
CREATE TABLE IF NOT EXISTS supplier_purchase (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    barber_id INT NULL,
    barbershop_id INT NULL,
    purchase_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    tools_description TEXT NOT NULL,
    total_paid DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_sp_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(id) ON DELETE RESTRICT,
    CONSTRAINT fk_sp_barber FOREIGN KEY (barber_id) REFERENCES barber(id) ON DELETE SET NULL,
    CONSTRAINT fk_sp_barbershop FOREIGN KEY (barbershop_id) REFERENCES barbershop(id) ON DELETE SET NULL
) ENGINE=InnoDB;

USE barbershop_db;

-- ============================================================
-- STORED PROCEDURES
-- Cada tabla tiene: listar, buscar por id, insertar, actualizar
-- y eliminar. Todas las validaciones lanzan SQLSTATE '45000'
-- con un mensaje legible para el usuario.
-- ============================================================

DELIMITER //

-- ============================================================
-- 0. HELPERS
-- ============================================================

DROP PROCEDURE IF EXISTS proc_raise //
CREATE PROCEDURE proc_raise(
    IN p_message VARCHAR(255)
)
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = p_message;
END //

-- ============================================================
-- 1. ROLE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_roles //
CREATE PROCEDURE proc_select_roles()
BEGIN
    SELECT id, name FROM role ORDER BY id ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_role_by_id //
CREATE PROCEDURE proc_select_role_by_id(
    IN p_id INT
)
BEGIN
    SELECT id, name FROM role WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_insert_role //
CREATE PROCEDURE proc_insert_role(
    IN p_name VARCHAR(50)
)
BEGIN
    IF TRIM(IFNULL(p_name, '')) = '' THEN
        CALL proc_raise('El nombre del rol es obligatorio.');
    END IF;
    IF EXISTS (SELECT 1 FROM role WHERE name = TRIM(p_name)) THEN
        CALL proc_raise('Ya existe un rol con ese nombre.');
    END IF;

    INSERT INTO role (name) VALUES (TRIM(p_name));
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_role //
CREATE PROCEDURE proc_update_role(
    IN p_id INT,
    IN p_name VARCHAR(50)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM role WHERE id = p_id) THEN
        CALL proc_raise('El rol indicado no existe.');
    END IF;
    IF TRIM(IFNULL(p_name, '')) = '' THEN
        CALL proc_raise('El nombre del rol es obligatorio.');
    END IF;
    IF EXISTS (SELECT 1 FROM role WHERE name = TRIM(p_name) AND id <> p_id) THEN
        CALL proc_raise('Ya existe otro rol con ese nombre.');
    END IF;

    UPDATE role SET name = TRIM(p_name) WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_role //
CREATE PROCEDURE proc_delete_role(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM role WHERE id = p_id) THEN
        CALL proc_raise('El rol indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM user WHERE role_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: hay usuarios con este rol.');
    END IF;

    DELETE FROM role WHERE id = p_id;
END //

-- ============================================================
-- 2. USER
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_users //
CREATE PROCEDURE proc_select_users()
BEGIN
    SELECT u.id, u.role_id, r.name AS role_name, u.full_name, u.email, u.phone, u.created_at
    FROM user u
    INNER JOIN role r ON u.role_id = r.id
    ORDER BY u.id ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_user_by_id //
CREATE PROCEDURE proc_select_user_by_id(
    IN p_id INT
)
BEGIN
    SELECT u.id, u.role_id, r.name AS role_name, u.full_name, u.email, u.phone, u.created_at
    FROM user u
    INNER JOIN role r ON u.role_id = r.id
    WHERE u.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_user //
CREATE PROCEDURE proc_validate_user(
    IN p_id INT,
    IN p_role_id INT,
    IN p_full_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM role WHERE id = p_role_id) THEN
        CALL proc_raise('El rol indicado no existe.');
    END IF;
    IF TRIM(IFNULL(p_full_name, '')) = '' THEN
        CALL proc_raise('El nombre completo es obligatorio.');
    END IF;
    IF TRIM(IFNULL(p_email, '')) NOT REGEXP '^[^@ ]+@[^@ ]+[.][^@ ]+$' THEN
        CALL proc_raise('El correo electrónico no es válido.');
    END IF;
    IF EXISTS (SELECT 1 FROM user WHERE email = TRIM(p_email) AND id <> IFNULL(p_id, 0)) THEN
        CALL proc_raise('Ya existe un usuario con ese correo electrónico.');
    END IF;
    IF TRIM(IFNULL(p_phone, '')) NOT REGEXP '^[0-9+() -]{7,20}$' THEN
        CALL proc_raise('El teléfono no es válido (7 a 20 dígitos).');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_user //
CREATE PROCEDURE proc_insert_user(
    IN p_role_id INT,
    IN p_full_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_password_hash VARCHAR(255),
    IN p_phone VARCHAR(20)
)
BEGIN
    CALL proc_validate_user(NULL, p_role_id, p_full_name, p_email, p_phone);
    IF TRIM(IFNULL(p_password_hash, '')) = '' THEN
        CALL proc_raise('La contraseña es obligatoria.');
    END IF;

    INSERT INTO user (role_id, full_name, email, password_hash, phone)
    VALUES (p_role_id, TRIM(p_full_name), TRIM(p_email), p_password_hash, TRIM(p_phone));
    SELECT LAST_INSERT_ID() AS id;
END //

-- p_password_hash NULL o vacío = conservar la contraseña actual
DROP PROCEDURE IF EXISTS proc_update_user //
CREATE PROCEDURE proc_update_user(
    IN p_id INT,
    IN p_role_id INT,
    IN p_full_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_password_hash VARCHAR(255),
    IN p_phone VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM user WHERE id = p_id) THEN
        CALL proc_raise('El usuario indicado no existe.');
    END IF;
    CALL proc_validate_user(p_id, p_role_id, p_full_name, p_email, p_phone);

    UPDATE user
    SET role_id = p_role_id,
        full_name = TRIM(p_full_name),
        email = TRIM(p_email),
        password_hash = IF(TRIM(IFNULL(p_password_hash, '')) = '', password_hash, p_password_hash),
        phone = TRIM(p_phone)
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_user //
CREATE PROCEDURE proc_delete_user(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM user WHERE id = p_id) THEN
        CALL proc_raise('El usuario indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM barbershop WHERE manager_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el usuario administra una barbería.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment WHERE customer_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el usuario tiene citas como cliente.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment a INNER JOIN barber b ON a.barber_id = b.id WHERE b.user_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el usuario es barbero y tiene citas registradas.');
    END IF;
    IF EXISTS (SELECT 1 FROM product_sale WHERE seller_user_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el usuario registró ventas.');
    END IF;
    IF EXISTS (SELECT 1 FROM product_sale_detail psd
               INNER JOIN product p ON psd.product_id = p.id
               INNER JOIN barber b ON p.barber_id = b.id
               WHERE b.user_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el usuario es barbero y tiene productos vendidos.');
    END IF;

    DELETE FROM user WHERE id = p_id;
END //

-- ============================================================
-- 3. BARBERSHOP
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_barbershops //
CREATE PROCEDURE proc_select_barbershops()
BEGIN
    SELECT b.id, b.manager_id, u.full_name AS manager_name, b.name, b.address, b.city, b.phone
    FROM barbershop b
    INNER JOIN user u ON b.manager_id = u.id
    ORDER BY b.id ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_barbershop_by_id //
CREATE PROCEDURE proc_select_barbershop_by_id(
    IN p_id INT
)
BEGIN
    SELECT b.id, b.manager_id, u.full_name AS manager_name, b.name, b.address, b.city, b.phone
    FROM barbershop b
    INNER JOIN user u ON b.manager_id = u.id
    WHERE b.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_barbershop //
CREATE PROCEDURE proc_validate_barbershop(
    IN p_manager_id INT,
    IN p_name VARCHAR(100),
    IN p_address VARCHAR(150),
    IN p_city VARCHAR(50),
    IN p_phone VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM user WHERE id = p_manager_id) THEN
        CALL proc_raise('El administrador indicado no existe.');
    END IF;
    IF TRIM(IFNULL(p_name, '')) = '' THEN
        CALL proc_raise('El nombre de la barbería es obligatorio.');
    END IF;
    IF TRIM(IFNULL(p_address, '')) = '' THEN
        CALL proc_raise('La dirección es obligatoria.');
    END IF;
    IF TRIM(IFNULL(p_city, '')) = '' THEN
        CALL proc_raise('La ciudad es obligatoria.');
    END IF;
    IF TRIM(IFNULL(p_phone, '')) NOT REGEXP '^[0-9+() -]{7,20}$' THEN
        CALL proc_raise('El teléfono no es válido (7 a 20 dígitos).');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_barbershop //
CREATE PROCEDURE proc_insert_barbershop(
    IN p_manager_id INT,
    IN p_name VARCHAR(100),
    IN p_address VARCHAR(150),
    IN p_city VARCHAR(50),
    IN p_phone VARCHAR(20)
)
BEGIN
    CALL proc_validate_barbershop(p_manager_id, p_name, p_address, p_city, p_phone);

    INSERT INTO barbershop (manager_id, name, address, city, phone)
    VALUES (p_manager_id, TRIM(p_name), TRIM(p_address), TRIM(p_city), TRIM(p_phone));
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_barbershop //
CREATE PROCEDURE proc_update_barbershop(
    IN p_id INT,
    IN p_manager_id INT,
    IN p_name VARCHAR(100),
    IN p_address VARCHAR(150),
    IN p_city VARCHAR(50),
    IN p_phone VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barbershop WHERE id = p_id) THEN
        CALL proc_raise('La barbería indicada no existe.');
    END IF;
    CALL proc_validate_barbershop(p_manager_id, p_name, p_address, p_city, p_phone);

    UPDATE barbershop
    SET manager_id = p_manager_id,
        name = TRIM(p_name),
        address = TRIM(p_address),
        city = TRIM(p_city),
        phone = TRIM(p_phone)
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_barbershop //
CREATE PROCEDURE proc_delete_barbershop(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barbershop WHERE id = p_id) THEN
        CALL proc_raise('La barbería indicada no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM product_sale_detail psd
               INNER JOIN product p ON psd.product_id = p.id
               WHERE p.barbershop_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: la barbería tiene productos con ventas registradas.');
    END IF;

    DELETE FROM barbershop WHERE id = p_id;
END //

-- ============================================================
-- 4. BARBER
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_barbers //
CREATE PROCEDURE proc_select_barbers()
BEGIN
    SELECT b.id, b.user_id, u.full_name AS barber_name, b.barbershop_id, bs.name AS barbershop_name,
           b.provides_home_service, b.provides_shop_service, b.commission_rate, b.is_active
    FROM barber b
    INNER JOIN user u ON b.user_id = u.id
    LEFT JOIN barbershop bs ON b.barbershop_id = bs.id
    ORDER BY b.id ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_barber_by_id //
CREATE PROCEDURE proc_select_barber_by_id(
    IN p_id INT
)
BEGIN
    SELECT b.id, b.user_id, u.full_name AS barber_name, b.barbershop_id, bs.name AS barbershop_name,
           b.provides_home_service, b.provides_shop_service, b.commission_rate, b.is_active
    FROM barber b
    INNER JOIN user u ON b.user_id = u.id
    LEFT JOIN barbershop bs ON b.barbershop_id = bs.id
    WHERE b.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_barber //
CREATE PROCEDURE proc_validate_barber(
    IN p_id INT,
    IN p_user_id INT,
    IN p_barbershop_id INT,
    IN p_provides_home_service TINYINT,
    IN p_provides_shop_service TINYINT,
    IN p_commission_rate DECIMAL(5,2)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM user WHERE id = p_user_id) THEN
        CALL proc_raise('El usuario indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM barber WHERE user_id = p_user_id AND id <> IFNULL(p_id, 0)) THEN
        CALL proc_raise('Ese usuario ya está registrado como barbero.');
    END IF;
    IF p_barbershop_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM barbershop WHERE id = p_barbershop_id) THEN
        CALL proc_raise('La barbería indicada no existe.');
    END IF;
    IF IFNULL(p_provides_home_service, -1) NOT IN (0, 1) OR IFNULL(p_provides_shop_service, -1) NOT IN (0, 1) THEN
        CALL proc_raise('Los tipos de servicio deben ser 0 (no) o 1 (sí).');
    END IF;
    IF p_provides_home_service = 0 AND p_provides_shop_service = 0 THEN
        CALL proc_raise('El barbero debe atender en barbería, a domicilio o ambos.');
    END IF;
    IF p_provides_shop_service = 1 AND p_barbershop_id IS NULL THEN
        CALL proc_raise('Si atiende en barbería debe indicar a qué barbería pertenece.');
    END IF;
    IF p_commission_rate IS NULL OR p_commission_rate < 0 OR p_commission_rate > 100 THEN
        CALL proc_raise('La comisión debe estar entre 0 y 100.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_barber //
CREATE PROCEDURE proc_insert_barber(
    IN p_user_id INT,
    IN p_barbershop_id INT,
    IN p_provides_home_service TINYINT,
    IN p_provides_shop_service TINYINT,
    IN p_commission_rate DECIMAL(5,2)
)
BEGIN
    CALL proc_validate_barber(NULL, p_user_id, p_barbershop_id, p_provides_home_service,
                              p_provides_shop_service, p_commission_rate);

    INSERT INTO barber (user_id, barbershop_id, provides_home_service, provides_shop_service, commission_rate)
    VALUES (p_user_id, p_barbershop_id, p_provides_home_service, p_provides_shop_service, p_commission_rate);
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_barber //
CREATE PROCEDURE proc_update_barber(
    IN p_id INT,
    IN p_user_id INT,
    IN p_barbershop_id INT,
    IN p_provides_home_service TINYINT,
    IN p_provides_shop_service TINYINT,
    IN p_commission_rate DECIMAL(5,2),
    IN p_is_active TINYINT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber WHERE id = p_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    CALL proc_validate_barber(p_id, p_user_id, p_barbershop_id, p_provides_home_service,
                              p_provides_shop_service, p_commission_rate);
    IF IFNULL(p_is_active, -1) NOT IN (0, 1) THEN
        CALL proc_raise('El estado activo debe ser 0 (no) o 1 (sí).');
    END IF;

    UPDATE barber
    SET user_id = p_user_id,
        barbershop_id = p_barbershop_id,
        provides_home_service = p_provides_home_service,
        provides_shop_service = p_provides_shop_service,
        commission_rate = p_commission_rate,
        is_active = p_is_active
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_barber //
CREATE PROCEDURE proc_delete_barber(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber WHERE id = p_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment WHERE barber_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el barbero tiene citas. Puede desactivarlo en su lugar.');
    END IF;
    IF EXISTS (SELECT 1 FROM product_sale_detail psd
               INNER JOIN product p ON psd.product_id = p.id
               WHERE p.barber_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el barbero tiene productos vendidos. Puede desactivarlo en su lugar.');
    END IF;

    DELETE FROM barber WHERE id = p_id;
END //

-- ============================================================
-- 5. BARBER SCHEDULE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_barber_schedule //
CREATE PROCEDURE proc_select_barber_schedule(
    IN p_barber_id INT
)
BEGIN
    SELECT id, barber_id, day_of_week, start_time, end_time, lunch_start_time, lunch_end_time
    FROM barber_schedule
    WHERE barber_id = p_barber_id
    ORDER BY FIELD(day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
END //

DROP PROCEDURE IF EXISTS proc_select_barber_schedule_by_id //
CREATE PROCEDURE proc_select_barber_schedule_by_id(
    IN p_id INT
)
BEGIN
    SELECT id, barber_id, day_of_week, start_time, end_time, lunch_start_time, lunch_end_time
    FROM barber_schedule
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_barber_schedule //
CREATE PROCEDURE proc_validate_barber_schedule(
    IN p_id INT,
    IN p_barber_id INT,
    IN p_day_of_week VARCHAR(10),
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_lunch_start_time TIME,
    IN p_lunch_end_time TIME
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber WHERE id = p_barber_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    IF IFNULL(p_day_of_week, '') NOT IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') THEN
        CALL proc_raise('El día de la semana no es válido.');
    END IF;
    IF p_start_time IS NULL OR p_end_time IS NULL THEN
        CALL proc_raise('La hora de entrada y de salida son obligatorias.');
    END IF;
    IF p_end_time <= p_start_time THEN
        CALL proc_raise('La hora de salida debe ser posterior a la de entrada.');
    END IF;
    IF (p_lunch_start_time IS NULL) <> (p_lunch_end_time IS NULL) THEN
        CALL proc_raise('Debe indicar ambas horas del almuerzo o ninguna.');
    END IF;
    IF p_lunch_start_time IS NOT NULL THEN
        IF p_lunch_end_time <= p_lunch_start_time THEN
            CALL proc_raise('El fin del almuerzo debe ser posterior a su inicio.');
        END IF;
        IF p_lunch_start_time < p_start_time OR p_lunch_end_time > p_end_time THEN
            CALL proc_raise('El almuerzo debe estar dentro del horario de trabajo.');
        END IF;
    END IF;
    IF EXISTS (SELECT 1 FROM barber_schedule
               WHERE barber_id = p_barber_id AND day_of_week = p_day_of_week AND id <> IFNULL(p_id, 0)) THEN
        CALL proc_raise('El barbero ya tiene un horario para ese día.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_barber_schedule //
CREATE PROCEDURE proc_insert_barber_schedule(
    IN p_barber_id INT,
    IN p_day_of_week VARCHAR(10),
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_lunch_start_time TIME,
    IN p_lunch_end_time TIME
)
BEGIN
    CALL proc_validate_barber_schedule(NULL, p_barber_id, p_day_of_week, p_start_time, p_end_time,
                                       p_lunch_start_time, p_lunch_end_time);

    INSERT INTO barber_schedule (barber_id, day_of_week, start_time, end_time, lunch_start_time, lunch_end_time)
    VALUES (p_barber_id, p_day_of_week, p_start_time, p_end_time, p_lunch_start_time, p_lunch_end_time);
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_barber_schedule //
CREATE PROCEDURE proc_update_barber_schedule(
    IN p_id INT,
    IN p_barber_id INT,
    IN p_day_of_week VARCHAR(10),
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_lunch_start_time TIME,
    IN p_lunch_end_time TIME
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber_schedule WHERE id = p_id) THEN
        CALL proc_raise('El horario indicado no existe.');
    END IF;
    CALL proc_validate_barber_schedule(p_id, p_barber_id, p_day_of_week, p_start_time, p_end_time,
                                       p_lunch_start_time, p_lunch_end_time);

    UPDATE barber_schedule
    SET barber_id = p_barber_id,
        day_of_week = p_day_of_week,
        start_time = p_start_time,
        end_time = p_end_time,
        lunch_start_time = p_lunch_start_time,
        lunch_end_time = p_lunch_end_time
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_barber_schedule //
CREATE PROCEDURE proc_delete_barber_schedule(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber_schedule WHERE id = p_id) THEN
        CALL proc_raise('El horario indicado no existe.');
    END IF;

    DELETE FROM barber_schedule WHERE id = p_id;
END //

-- ============================================================
-- 6. SCHEDULE BLOCK
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_schedule_blocks //
CREATE PROCEDURE proc_select_schedule_blocks(
    IN p_barber_id INT
)
BEGIN
    SELECT id, barber_id, start_datetime, end_datetime, reason
    FROM schedule_block
    WHERE barber_id = p_barber_id
    ORDER BY start_datetime ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_schedule_block_by_id //
CREATE PROCEDURE proc_select_schedule_block_by_id(
    IN p_id INT
)
BEGIN
    SELECT id, barber_id, start_datetime, end_datetime, reason
    FROM schedule_block
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_schedule_block //
CREATE PROCEDURE proc_validate_schedule_block(
    IN p_id INT,
    IN p_barber_id INT,
    IN p_start_datetime DATETIME,
    IN p_end_datetime DATETIME
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber WHERE id = p_barber_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    IF p_start_datetime IS NULL OR p_end_datetime IS NULL THEN
        CALL proc_raise('La fecha/hora de inicio y fin son obligatorias.');
    END IF;
    IF p_end_datetime <= p_start_datetime THEN
        CALL proc_raise('El fin del bloqueo debe ser posterior a su inicio.');
    END IF;
    IF EXISTS (SELECT 1 FROM schedule_block
               WHERE barber_id = p_barber_id AND id <> IFNULL(p_id, 0)
                 AND start_datetime < p_end_datetime AND end_datetime > p_start_datetime) THEN
        CALL proc_raise('El bloqueo se cruza con otro bloqueo del barbero.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment
               WHERE barber_id = p_barber_id AND status IN ('Pending', 'Confirmed')
                 AND TIMESTAMP(appointment_date, start_time) < p_end_datetime
                 AND TIMESTAMP(appointment_date, end_time) > p_start_datetime) THEN
        CALL proc_raise('El bloqueo se cruza con citas pendientes o confirmadas del barbero.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_schedule_block //
CREATE PROCEDURE proc_insert_schedule_block(
    IN p_barber_id INT,
    IN p_start_datetime DATETIME,
    IN p_end_datetime DATETIME,
    IN p_reason VARCHAR(255)
)
BEGIN
    CALL proc_validate_schedule_block(NULL, p_barber_id, p_start_datetime, p_end_datetime);

    INSERT INTO schedule_block (barber_id, start_datetime, end_datetime, reason)
    VALUES (p_barber_id, p_start_datetime, p_end_datetime, NULLIF(TRIM(p_reason), ''));
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_schedule_block //
CREATE PROCEDURE proc_update_schedule_block(
    IN p_id INT,
    IN p_barber_id INT,
    IN p_start_datetime DATETIME,
    IN p_end_datetime DATETIME,
    IN p_reason VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schedule_block WHERE id = p_id) THEN
        CALL proc_raise('El bloqueo indicado no existe.');
    END IF;
    CALL proc_validate_schedule_block(p_id, p_barber_id, p_start_datetime, p_end_datetime);

    UPDATE schedule_block
    SET barber_id = p_barber_id,
        start_datetime = p_start_datetime,
        end_datetime = p_end_datetime,
        reason = NULLIF(TRIM(p_reason), '')
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_schedule_block //
CREATE PROCEDURE proc_delete_schedule_block(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schedule_block WHERE id = p_id) THEN
        CALL proc_raise('El bloqueo indicado no existe.');
    END IF;

    DELETE FROM schedule_block WHERE id = p_id;
END //

-- ============================================================
-- 7. SERVICE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_services //
CREATE PROCEDURE proc_select_services()
BEGIN
    SELECT id, name, description, base_price, duration_minutes, buffer_minutes
    FROM service
    ORDER BY name ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_service_by_id //
CREATE PROCEDURE proc_select_service_by_id(
    IN p_id INT
)
BEGIN
    SELECT id, name, description, base_price, duration_minutes, buffer_minutes
    FROM service
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_service //
CREATE PROCEDURE proc_validate_service(
    IN p_id INT,
    IN p_name VARCHAR(100),
    IN p_base_price DECIMAL(10,2),
    IN p_duration_minutes INT,
    IN p_buffer_minutes INT
)
BEGIN
    IF TRIM(IFNULL(p_name, '')) = '' THEN
        CALL proc_raise('El nombre del servicio es obligatorio.');
    END IF;
    IF EXISTS (SELECT 1 FROM service WHERE name = TRIM(p_name) AND id <> IFNULL(p_id, 0)) THEN
        CALL proc_raise('Ya existe un servicio con ese nombre.');
    END IF;
    IF p_base_price IS NULL OR p_base_price < 0 THEN
        CALL proc_raise('El precio base no puede ser negativo.');
    END IF;
    IF p_duration_minutes IS NULL OR p_duration_minutes <= 0 THEN
        CALL proc_raise('La duración debe ser mayor a 0 minutos.');
    END IF;
    IF p_buffer_minutes IS NOT NULL AND p_buffer_minutes < 0 THEN
        CALL proc_raise('El tiempo de preparación no puede ser negativo.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_service //
CREATE PROCEDURE proc_insert_service(
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_base_price DECIMAL(10,2),
    IN p_duration_minutes INT,
    IN p_buffer_minutes INT
)
BEGIN
    CALL proc_validate_service(NULL, p_name, p_base_price, p_duration_minutes, p_buffer_minutes);

    INSERT INTO service (name, description, base_price, duration_minutes, buffer_minutes)
    VALUES (TRIM(p_name), NULLIF(TRIM(p_description), ''), p_base_price, p_duration_minutes, IFNULL(p_buffer_minutes, 10));
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_service //
CREATE PROCEDURE proc_update_service(
    IN p_id INT,
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_base_price DECIMAL(10,2),
    IN p_duration_minutes INT,
    IN p_buffer_minutes INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM service WHERE id = p_id) THEN
        CALL proc_raise('El servicio indicado no existe.');
    END IF;
    CALL proc_validate_service(p_id, p_name, p_base_price, p_duration_minutes, p_buffer_minutes);

    UPDATE service
    SET name = TRIM(p_name),
        description = NULLIF(TRIM(p_description), ''),
        base_price = p_base_price,
        duration_minutes = p_duration_minutes,
        buffer_minutes = IFNULL(p_buffer_minutes, 10)
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_service //
CREATE PROCEDURE proc_delete_service(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM service WHERE id = p_id) THEN
        CALL proc_raise('El servicio indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment_service_detail WHERE service_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el servicio está registrado en citas.');
    END IF;

    DELETE FROM service WHERE id = p_id;
END //

-- ============================================================
-- 8. BARBER SERVICE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_barber_services //
CREATE PROCEDURE proc_select_barber_services(
    IN p_barber_id INT
)
BEGIN
    SELECT bs.id, bs.barber_id, bs.service_id, s.name AS service_name,
           bs.custom_price, bs.custom_duration_minutes,
           COALESCE(bs.custom_price, s.base_price) AS final_price,
           COALESCE(bs.custom_duration_minutes, s.duration_minutes) AS final_duration
    FROM barber_service bs
    INNER JOIN service s ON bs.service_id = s.id
    WHERE bs.barber_id = p_barber_id
    ORDER BY s.name ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_barber_service_by_id //
CREATE PROCEDURE proc_select_barber_service_by_id(
    IN p_id INT
)
BEGIN
    SELECT bs.id, bs.barber_id, bs.service_id, s.name AS service_name,
           bs.custom_price, bs.custom_duration_minutes,
           COALESCE(bs.custom_price, s.base_price) AS final_price,
           COALESCE(bs.custom_duration_minutes, s.duration_minutes) AS final_duration
    FROM barber_service bs
    INNER JOIN service s ON bs.service_id = s.id
    WHERE bs.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_barber_service //
CREATE PROCEDURE proc_validate_barber_service(
    IN p_id INT,
    IN p_barber_id INT,
    IN p_service_id INT,
    IN p_custom_price DECIMAL(10,2),
    IN p_custom_duration_minutes INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber WHERE id = p_barber_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM service WHERE id = p_service_id) THEN
        CALL proc_raise('El servicio indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM barber_service
               WHERE barber_id = p_barber_id AND service_id = p_service_id AND id <> IFNULL(p_id, 0)) THEN
        CALL proc_raise('El barbero ya tiene asignado ese servicio.');
    END IF;
    IF p_custom_price IS NOT NULL AND p_custom_price < 0 THEN
        CALL proc_raise('El precio personalizado no puede ser negativo.');
    END IF;
    IF p_custom_duration_minutes IS NOT NULL AND p_custom_duration_minutes <= 0 THEN
        CALL proc_raise('La duración personalizada debe ser mayor a 0 minutos.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_barber_service //
CREATE PROCEDURE proc_insert_barber_service(
    IN p_barber_id INT,
    IN p_service_id INT,
    IN p_custom_price DECIMAL(10,2),
    IN p_custom_duration_minutes INT
)
BEGIN
    CALL proc_validate_barber_service(NULL, p_barber_id, p_service_id, p_custom_price, p_custom_duration_minutes);

    INSERT INTO barber_service (barber_id, service_id, custom_price, custom_duration_minutes)
    VALUES (p_barber_id, p_service_id, p_custom_price, p_custom_duration_minutes);
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_barber_service //
CREATE PROCEDURE proc_update_barber_service(
    IN p_id INT,
    IN p_barber_id INT,
    IN p_service_id INT,
    IN p_custom_price DECIMAL(10,2),
    IN p_custom_duration_minutes INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber_service WHERE id = p_id) THEN
        CALL proc_raise('La asignación de servicio indicada no existe.');
    END IF;
    CALL proc_validate_barber_service(p_id, p_barber_id, p_service_id, p_custom_price, p_custom_duration_minutes);

    UPDATE barber_service
    SET barber_id = p_barber_id,
        service_id = p_service_id,
        custom_price = p_custom_price,
        custom_duration_minutes = p_custom_duration_minutes
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_barber_service //
CREATE PROCEDURE proc_delete_barber_service(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM barber_service WHERE id = p_id) THEN
        CALL proc_raise('La asignación de servicio indicada no existe.');
    END IF;

    DELETE FROM barber_service WHERE id = p_id;
END //

-- ============================================================
-- 9. APPOINTMENT
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_appointments //
CREATE PROCEDURE proc_select_appointments()
BEGIN
    SELECT a.id, a.customer_id, uc.full_name AS customer_name, a.barber_id, ub.full_name AS barber_name,
           a.barbershop_id, a.appointment_date, a.start_time, a.end_time, a.location_type,
           a.home_address, a.status, a.total_amount
    FROM appointment a
    INNER JOIN user uc ON a.customer_id = uc.id
    INNER JOIN barber b ON a.barber_id = b.id
    INNER JOIN user ub ON b.user_id = ub.id
    ORDER BY a.appointment_date DESC, a.start_time DESC;
END //

DROP PROCEDURE IF EXISTS proc_select_appointment_by_id //
CREATE PROCEDURE proc_select_appointment_by_id(
    IN p_id INT
)
BEGIN
    SELECT a.id, a.customer_id, uc.full_name AS customer_name, a.barber_id, ub.full_name AS barber_name,
           a.barbershop_id, a.appointment_date, a.start_time, a.end_time, a.location_type,
           a.home_address, a.status, a.total_amount
    FROM appointment a
    INNER JOIN user uc ON a.customer_id = uc.id
    INNER JOIN barber b ON a.barber_id = b.id
    INNER JOIN user ub ON b.user_id = ub.id
    WHERE a.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_select_appointments_by_customer //
CREATE PROCEDURE proc_select_appointments_by_customer(
    IN p_customer_id INT
)
BEGIN
    SELECT a.id, a.customer_id, a.barber_id, u.full_name AS barber_name, a.barbershop_id,
           a.appointment_date, a.start_time, a.end_time, a.location_type, a.home_address, a.status, a.total_amount
    FROM appointment a
    INNER JOIN barber b ON a.barber_id = b.id
    INNER JOIN user u ON b.user_id = u.id
    WHERE a.customer_id = p_customer_id
    ORDER BY a.appointment_date DESC, a.start_time DESC;
END //

DROP PROCEDURE IF EXISTS proc_select_appointments_by_barber //
CREATE PROCEDURE proc_select_appointments_by_barber(
    IN p_barber_id INT
)
BEGIN
    SELECT a.id, a.customer_id, u.full_name AS customer_name, a.barber_id, a.barbershop_id,
           a.appointment_date, a.start_time, a.end_time, a.location_type, a.home_address, a.status, a.total_amount
    FROM appointment a
    INNER JOIN user u ON a.customer_id = u.id
    WHERE a.barber_id = p_barber_id
    ORDER BY a.appointment_date DESC, a.start_time DESC;
END //

-- Valida una cita nueva (p_appointment_id NULL) o existente.
-- Completa p_barbershop_id con la barbería del barbero si es 'Shop'
-- y limpia el campo que no corresponde al tipo de ubicación.
DROP PROCEDURE IF EXISTS proc_validate_appointment //
CREATE PROCEDURE proc_validate_appointment(
    IN p_appointment_id INT,
    IN p_customer_id INT,
    IN p_barber_id INT,
    INOUT p_barbershop_id INT,
    IN p_appointment_date DATE,
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_location_type VARCHAR(10),
    INOUT p_home_address VARCHAR(200)
)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_barber_shop_id INT;
    DECLARE v_home TINYINT;
    DECLARE v_shop TINYINT;
    DECLARE v_active TINYINT;
    DECLARE v_day VARCHAR(10);

    IF NOT EXISTS (SELECT 1 FROM user WHERE id = p_customer_id) THEN
        CALL proc_raise('El cliente indicado no existe.');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM barber WHERE id = p_barber_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;

    SELECT user_id, barbershop_id, provides_home_service, provides_shop_service, is_active
    INTO v_user_id, v_barber_shop_id, v_home, v_shop, v_active
    FROM barber WHERE id = p_barber_id;

    IF v_active <> 1 THEN
        CALL proc_raise('El barbero está inactivo.');
    END IF;
    IF v_user_id = p_customer_id THEN
        CALL proc_raise('El cliente no puede ser el mismo barbero.');
    END IF;
    IF p_appointment_date IS NULL OR p_start_time IS NULL OR p_end_time IS NULL THEN
        CALL proc_raise('La fecha, hora de inicio y hora de fin son obligatorias.');
    END IF;
    IF p_end_time <= p_start_time THEN
        CALL proc_raise('La hora de fin debe ser posterior a la hora de inicio.');
    END IF;
    IF TIMESTAMP(p_appointment_date, p_start_time) <= NOW() THEN
        CALL proc_raise('No se pueden agendar citas en el pasado.');
    END IF;

    IF p_location_type = 'Shop' THEN
        IF v_shop <> 1 THEN
            CALL proc_raise('El barbero no atiende en barbería.');
        END IF;
        SET p_barbershop_id = IFNULL(p_barbershop_id, v_barber_shop_id);
        IF p_barbershop_id IS NULL THEN
            CALL proc_raise('Debe indicar la barbería de la cita.');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM barbershop WHERE id = p_barbershop_id) THEN
            CALL proc_raise('La barbería indicada no existe.');
        END IF;
        IF v_barber_shop_id IS NOT NULL AND v_barber_shop_id <> p_barbershop_id THEN
            CALL proc_raise('El barbero no trabaja en esa barbería.');
        END IF;
        SET p_home_address = NULL;
    ELSEIF p_location_type = 'Home' THEN
        IF v_home <> 1 THEN
            CALL proc_raise('El barbero no ofrece servicio a domicilio.');
        END IF;
        IF TRIM(IFNULL(p_home_address, '')) = '' THEN
            CALL proc_raise('Debe indicar la dirección para el servicio a domicilio.');
        END IF;
        SET p_home_address = TRIM(p_home_address);
        SET p_barbershop_id = NULL;
    ELSE
        CALL proc_raise('El tipo de ubicación debe ser Shop o Home.');
    END IF;

    -- Si el barbero tiene horarios cargados, la cita debe respetarlos
    IF EXISTS (SELECT 1 FROM barber_schedule WHERE barber_id = p_barber_id) THEN
        SET v_day = ELT(WEEKDAY(p_appointment_date) + 1,
                        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
        IF NOT EXISTS (SELECT 1 FROM barber_schedule
                       WHERE barber_id = p_barber_id AND day_of_week = v_day
                         AND p_start_time >= start_time AND p_end_time <= end_time) THEN
            CALL proc_raise('La cita está fuera del horario de trabajo del barbero.');
        END IF;
        IF EXISTS (SELECT 1 FROM barber_schedule
                   WHERE barber_id = p_barber_id AND day_of_week = v_day
                     AND lunch_start_time IS NOT NULL
                     AND p_start_time < lunch_end_time AND p_end_time > lunch_start_time) THEN
            CALL proc_raise('La cita coincide con la hora de almuerzo del barbero.');
        END IF;
    END IF;

    IF EXISTS (SELECT 1 FROM schedule_block
               WHERE barber_id = p_barber_id
                 AND start_datetime < TIMESTAMP(p_appointment_date, p_end_time)
                 AND end_datetime > TIMESTAMP(p_appointment_date, p_start_time)) THEN
        CALL proc_raise('El barbero tiene un bloqueo de agenda en ese horario.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment
               WHERE barber_id = p_barber_id AND id <> IFNULL(p_appointment_id, 0)
                 AND status IN ('Pending', 'Confirmed')
                 AND appointment_date = p_appointment_date
                 AND start_time < p_end_time AND end_time > p_start_time) THEN
        CALL proc_raise('El barbero ya tiene otra cita en ese horario.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment
               WHERE customer_id = p_customer_id AND id <> IFNULL(p_appointment_id, 0)
                 AND status IN ('Pending', 'Confirmed')
                 AND appointment_date = p_appointment_date
                 AND start_time < p_end_time AND end_time > p_start_time) THEN
        CALL proc_raise('El cliente ya tiene otra cita en ese horario.');
    END IF;
END //

-- El total inicia en 0 y se recalcula al agregar servicios (appointment_service_detail)
DROP PROCEDURE IF EXISTS proc_insert_appointment //
CREATE PROCEDURE proc_insert_appointment(
    IN p_customer_id INT,
    IN p_barber_id INT,
    IN p_barbershop_id INT,
    IN p_appointment_date DATE,
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_location_type VARCHAR(10),
    IN p_home_address VARCHAR(200)
)
BEGIN
    CALL proc_validate_appointment(NULL, p_customer_id, p_barber_id, p_barbershop_id, p_appointment_date,
                                   p_start_time, p_end_time, p_location_type, p_home_address);

    INSERT INTO appointment (customer_id, barber_id, barbershop_id, appointment_date, start_time, end_time,
                             location_type, home_address, total_amount)
    VALUES (p_customer_id, p_barber_id, p_barbershop_id, p_appointment_date, p_start_time, p_end_time,
            p_location_type, p_home_address, 0);
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_appointment //
CREATE PROCEDURE proc_update_appointment(
    IN p_id INT,
    IN p_customer_id INT,
    IN p_barber_id INT,
    IN p_barbershop_id INT,
    IN p_appointment_date DATE,
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_location_type VARCHAR(10),
    IN p_home_address VARCHAR(200)
)
BEGIN
    DECLARE v_status VARCHAR(10);

    SELECT status INTO v_status FROM appointment WHERE id = p_id;
    IF v_status IS NULL THEN
        CALL proc_raise('La cita indicada no existe.');
    END IF;
    IF v_status NOT IN ('Pending', 'Confirmed') THEN
        CALL proc_raise('Solo se pueden modificar citas pendientes o confirmadas.');
    END IF;
    CALL proc_validate_appointment(p_id, p_customer_id, p_barber_id, p_barbershop_id, p_appointment_date,
                                   p_start_time, p_end_time, p_location_type, p_home_address);

    UPDATE appointment
    SET customer_id = p_customer_id,
        barber_id = p_barber_id,
        barbershop_id = p_barbershop_id,
        appointment_date = p_appointment_date,
        start_time = p_start_time,
        end_time = p_end_time,
        location_type = p_location_type,
        home_address = p_home_address
    WHERE id = p_id;
END //

-- Transiciones permitidas:
--   Pending   -> Confirmed | Cancelled
--   Confirmed -> Completed | Cancelled
DROP PROCEDURE IF EXISTS proc_update_appointment_status //
CREATE PROCEDURE proc_update_appointment_status(
    IN p_appointment_id INT,
    IN p_new_status VARCHAR(10)
)
BEGIN
    DECLARE v_status VARCHAR(10);

    SELECT status INTO v_status FROM appointment WHERE id = p_appointment_id;
    IF v_status IS NULL THEN
        CALL proc_raise('La cita indicada no existe.');
    END IF;
    IF IFNULL(p_new_status, '') NOT IN ('Pending', 'Confirmed', 'Completed', 'Cancelled') THEN
        CALL proc_raise('El estado no es válido.');
    END IF;
    IF v_status = p_new_status THEN
        CALL proc_raise('La cita ya tiene ese estado.');
    END IF;
    IF v_status IN ('Completed', 'Cancelled') THEN
        CALL proc_raise('La cita ya fue completada o cancelada; no se puede cambiar su estado.');
    END IF;
    IF v_status = 'Pending' AND p_new_status NOT IN ('Confirmed', 'Cancelled') THEN
        CALL proc_raise('Una cita pendiente solo puede confirmarse o cancelarse.');
    END IF;
    IF v_status = 'Confirmed' AND p_new_status NOT IN ('Completed', 'Cancelled') THEN
        CALL proc_raise('Una cita confirmada solo puede completarse o cancelarse.');
    END IF;
    IF p_new_status = 'Completed'
       AND NOT EXISTS (SELECT 1 FROM appointment_service_detail WHERE appointment_id = p_appointment_id) THEN
        CALL proc_raise('No se puede completar una cita sin servicios registrados.');
    END IF;

    UPDATE appointment
    SET status = p_new_status
    WHERE id = p_appointment_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_appointment //
CREATE PROCEDURE proc_delete_appointment(
    IN p_id INT
)
BEGIN
    DECLARE v_status VARCHAR(10);

    SELECT status INTO v_status FROM appointment WHERE id = p_id;
    IF v_status IS NULL THEN
        CALL proc_raise('La cita indicada no existe.');
    END IF;
    IF v_status IN ('Confirmed', 'Completed') THEN
        CALL proc_raise('Solo se pueden eliminar citas pendientes o canceladas.');
    END IF;

    DELETE FROM appointment WHERE id = p_id;
END //

-- ============================================================
-- 10. APPOINTMENT SERVICE DETAIL
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_appointment_details //
CREATE PROCEDURE proc_select_appointment_details(
    IN p_appointment_id INT
)
BEGIN
    SELECT asd.id, asd.appointment_id, asd.service_id, s.name AS service_name, asd.applied_price, asd.applied_duration_minutes
    FROM appointment_service_detail asd
    INNER JOIN service s ON asd.service_id = s.id
    WHERE asd.appointment_id = p_appointment_id;
END //

DROP PROCEDURE IF EXISTS proc_select_appointment_detail_by_id //
CREATE PROCEDURE proc_select_appointment_detail_by_id(
    IN p_id INT
)
BEGIN
    SELECT asd.id, asd.appointment_id, asd.service_id, s.name AS service_name, asd.applied_price, asd.applied_duration_minutes
    FROM appointment_service_detail asd
    INNER JOIN service s ON asd.service_id = s.id
    WHERE asd.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_recalculate_appointment_total //
CREATE PROCEDURE proc_recalculate_appointment_total(
    IN p_appointment_id INT
)
BEGIN
    UPDATE appointment
    SET total_amount = (SELECT IFNULL(SUM(applied_price), 0)
                        FROM appointment_service_detail
                        WHERE appointment_id = p_appointment_id)
    WHERE id = p_appointment_id;
END //

DROP PROCEDURE IF EXISTS proc_check_appointment_editable //
CREATE PROCEDURE proc_check_appointment_editable(
    IN p_appointment_id INT
)
BEGIN
    DECLARE v_status VARCHAR(10);

    SELECT status INTO v_status FROM appointment WHERE id = p_appointment_id;
    IF v_status IS NULL THEN
        CALL proc_raise('La cita indicada no existe.');
    END IF;
    IF v_status NOT IN ('Pending', 'Confirmed') THEN
        CALL proc_raise('Solo se pueden modificar los servicios de citas pendientes o confirmadas.');
    END IF;
END //

-- Precio y duración NULL = se toman del barbero (barber_service) o del servicio
DROP PROCEDURE IF EXISTS proc_insert_appointment_detail //
CREATE PROCEDURE proc_insert_appointment_detail(
    IN p_appointment_id INT,
    IN p_service_id INT,
    IN p_applied_price DECIMAL(10,2),
    IN p_applied_duration_minutes INT
)
BEGIN
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_duration INT;
    DECLARE v_new_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    CALL proc_check_appointment_editable(p_appointment_id);
    IF NOT EXISTS (SELECT 1 FROM service WHERE id = p_service_id) THEN
        CALL proc_raise('El servicio indicado no existe.');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM barber_service bs
                   INNER JOIN appointment a ON a.barber_id = bs.barber_id
                   WHERE a.id = p_appointment_id AND bs.service_id = p_service_id) THEN
        CALL proc_raise('El barbero de la cita no ofrece ese servicio.');
    END IF;
    IF EXISTS (SELECT 1 FROM appointment_service_detail
               WHERE appointment_id = p_appointment_id AND service_id = p_service_id) THEN
        CALL proc_raise('Ese servicio ya está agregado a la cita.');
    END IF;
    IF p_applied_price IS NOT NULL AND p_applied_price < 0 THEN
        CALL proc_raise('El precio no puede ser negativo.');
    END IF;
    IF p_applied_duration_minutes IS NOT NULL AND p_applied_duration_minutes <= 0 THEN
        CALL proc_raise('La duración debe ser mayor a 0 minutos.');
    END IF;

    SELECT COALESCE(p_applied_price, bs.custom_price, s.base_price),
           COALESCE(p_applied_duration_minutes, bs.custom_duration_minutes, s.duration_minutes)
    INTO v_price, v_duration
    FROM service s
    INNER JOIN appointment a ON a.id = p_appointment_id
    INNER JOIN barber_service bs ON bs.barber_id = a.barber_id AND bs.service_id = s.id
    WHERE s.id = p_service_id;

    START TRANSACTION;
    INSERT INTO appointment_service_detail (appointment_id, service_id, applied_price, applied_duration_minutes)
    VALUES (p_appointment_id, p_service_id, v_price, v_duration);
    SET v_new_id = LAST_INSERT_ID();
    CALL proc_recalculate_appointment_total(p_appointment_id);
    COMMIT;

    SELECT v_new_id AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_appointment_detail //
CREATE PROCEDURE proc_update_appointment_detail(
    IN p_id INT,
    IN p_applied_price DECIMAL(10,2),
    IN p_applied_duration_minutes INT
)
BEGIN
    DECLARE v_appointment_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT appointment_id INTO v_appointment_id FROM appointment_service_detail WHERE id = p_id;
    IF v_appointment_id IS NULL THEN
        CALL proc_raise('El detalle indicado no existe.');
    END IF;
    CALL proc_check_appointment_editable(v_appointment_id);
    IF p_applied_price IS NULL OR p_applied_price < 0 THEN
        CALL proc_raise('El precio no puede ser negativo.');
    END IF;
    IF p_applied_duration_minutes IS NULL OR p_applied_duration_minutes <= 0 THEN
        CALL proc_raise('La duración debe ser mayor a 0 minutos.');
    END IF;

    START TRANSACTION;
    UPDATE appointment_service_detail
    SET applied_price = p_applied_price,
        applied_duration_minutes = p_applied_duration_minutes
    WHERE id = p_id;
    CALL proc_recalculate_appointment_total(v_appointment_id);
    COMMIT;
END //

DROP PROCEDURE IF EXISTS proc_delete_appointment_detail //
CREATE PROCEDURE proc_delete_appointment_detail(
    IN p_id INT
)
BEGIN
    DECLARE v_appointment_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT appointment_id INTO v_appointment_id FROM appointment_service_detail WHERE id = p_id;
    IF v_appointment_id IS NULL THEN
        CALL proc_raise('El detalle indicado no existe.');
    END IF;
    CALL proc_check_appointment_editable(v_appointment_id);

    START TRANSACTION;
    DELETE FROM appointment_service_detail WHERE id = p_id;
    CALL proc_recalculate_appointment_total(v_appointment_id);
    COMMIT;
END //

-- ============================================================
-- 11. PRODUCT
-- ============================================================

-- Productos disponibles (con stock)
DROP PROCEDURE IF EXISTS proc_select_products //
CREATE PROCEDURE proc_select_products()
BEGIN
    SELECT p.id, p.barbershop_id, bs.name AS barbershop_name, p.barber_id, u.full_name AS barber_name,
           p.name, p.description, p.selling_price, p.stock_quantity, p.min_stock_level
    FROM product p
    LEFT JOIN barbershop bs ON p.barbershop_id = bs.id
    LEFT JOIN barber b ON p.barber_id = b.id
    LEFT JOIN user u ON b.user_id = u.id
    WHERE p.stock_quantity > 0
    ORDER BY p.name ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_all_products //
CREATE PROCEDURE proc_select_all_products()
BEGIN
    SELECT p.id, p.barbershop_id, bs.name AS barbershop_name, p.barber_id, u.full_name AS barber_name,
           p.name, p.description, p.selling_price, p.stock_quantity, p.min_stock_level
    FROM product p
    LEFT JOIN barbershop bs ON p.barbershop_id = bs.id
    LEFT JOIN barber b ON p.barber_id = b.id
    LEFT JOIN user u ON b.user_id = u.id
    ORDER BY p.name ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_low_stock_products //
CREATE PROCEDURE proc_select_low_stock_products()
BEGIN
    SELECT p.id, p.barbershop_id, bs.name AS barbershop_name, p.barber_id, u.full_name AS barber_name,
           p.name, p.description, p.selling_price, p.stock_quantity, p.min_stock_level
    FROM product p
    LEFT JOIN barbershop bs ON p.barbershop_id = bs.id
    LEFT JOIN barber b ON p.barber_id = b.id
    LEFT JOIN user u ON b.user_id = u.id
    WHERE p.stock_quantity <= p.min_stock_level
    ORDER BY p.stock_quantity ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_product_by_id //
CREATE PROCEDURE proc_select_product_by_id(
    IN p_id INT
)
BEGIN
    SELECT p.id, p.barbershop_id, bs.name AS barbershop_name, p.barber_id, u.full_name AS barber_name,
           p.name, p.description, p.selling_price, p.stock_quantity, p.min_stock_level
    FROM product p
    LEFT JOIN barbershop bs ON p.barbershop_id = bs.id
    LEFT JOIN barber b ON p.barber_id = b.id
    LEFT JOIN user u ON b.user_id = u.id
    WHERE p.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_product //
CREATE PROCEDURE proc_validate_product(
    IN p_barbershop_id INT,
    IN p_barber_id INT,
    IN p_name VARCHAR(100),
    IN p_selling_price DECIMAL(10,2),
    IN p_stock_quantity INT,
    IN p_min_stock_level INT
)
BEGIN
    IF p_barbershop_id IS NULL AND p_barber_id IS NULL THEN
        CALL proc_raise('El producto debe pertenecer a una barbería o a un barbero.');
    END IF;
    IF p_barbershop_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM barbershop WHERE id = p_barbershop_id) THEN
        CALL proc_raise('La barbería indicada no existe.');
    END IF;
    IF p_barber_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM barber WHERE id = p_barber_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    IF TRIM(IFNULL(p_name, '')) = '' THEN
        CALL proc_raise('El nombre del producto es obligatorio.');
    END IF;
    IF p_selling_price IS NULL OR p_selling_price < 0 THEN
        CALL proc_raise('El precio de venta no puede ser negativo.');
    END IF;
    IF p_stock_quantity IS NULL OR p_stock_quantity < 0 THEN
        CALL proc_raise('El stock no puede ser negativo.');
    END IF;
    IF p_min_stock_level IS NOT NULL AND p_min_stock_level < 0 THEN
        CALL proc_raise('El stock mínimo no puede ser negativo.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_product //
CREATE PROCEDURE proc_insert_product(
    IN p_barbershop_id INT,
    IN p_barber_id INT,
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_selling_price DECIMAL(10,2),
    IN p_stock_quantity INT,
    IN p_min_stock_level INT
)
BEGIN
    CALL proc_validate_product(p_barbershop_id, p_barber_id, p_name, p_selling_price,
                               p_stock_quantity, p_min_stock_level);

    INSERT INTO product (barbershop_id, barber_id, name, description, selling_price, stock_quantity, min_stock_level)
    VALUES (p_barbershop_id, p_barber_id, TRIM(p_name), NULLIF(TRIM(p_description), ''), p_selling_price,
            p_stock_quantity, IFNULL(p_min_stock_level, 5));
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_product //
CREATE PROCEDURE proc_update_product(
    IN p_id INT,
    IN p_barbershop_id INT,
    IN p_barber_id INT,
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_selling_price DECIMAL(10,2),
    IN p_stock_quantity INT,
    IN p_min_stock_level INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM product WHERE id = p_id) THEN
        CALL proc_raise('El producto indicado no existe.');
    END IF;
    CALL proc_validate_product(p_barbershop_id, p_barber_id, p_name, p_selling_price,
                               p_stock_quantity, p_min_stock_level);

    UPDATE product
    SET barbershop_id = p_barbershop_id,
        barber_id = p_barber_id,
        name = TRIM(p_name),
        description = NULLIF(TRIM(p_description), ''),
        selling_price = p_selling_price,
        stock_quantity = p_stock_quantity,
        min_stock_level = IFNULL(p_min_stock_level, 5)
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_product //
CREATE PROCEDURE proc_delete_product(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM product WHERE id = p_id) THEN
        CALL proc_raise('El producto indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM product_sale_detail WHERE product_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el producto tiene ventas registradas.');
    END IF;

    DELETE FROM product WHERE id = p_id;
END //

-- ============================================================
-- 12. PRODUCT SALE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_product_sales //
CREATE PROCEDURE proc_select_product_sales()
BEGIN
    SELECT ps.id, ps.customer_id, u_cust.full_name AS customer_name, ps.seller_user_id, u_sell.full_name AS seller_name,
           ps.sale_datetime, ps.total_amount, ps.payment_method
    FROM product_sale ps
    LEFT JOIN user u_cust ON ps.customer_id = u_cust.id
    INNER JOIN user u_sell ON ps.seller_user_id = u_sell.id
    ORDER BY ps.sale_datetime DESC;
END //

DROP PROCEDURE IF EXISTS proc_select_product_sale_by_id //
CREATE PROCEDURE proc_select_product_sale_by_id(
    IN p_id INT
)
BEGIN
    SELECT ps.id, ps.customer_id, u_cust.full_name AS customer_name, ps.seller_user_id, u_sell.full_name AS seller_name,
           ps.sale_datetime, ps.total_amount, ps.payment_method
    FROM product_sale ps
    LEFT JOIN user u_cust ON ps.customer_id = u_cust.id
    INNER JOIN user u_sell ON ps.seller_user_id = u_sell.id
    WHERE ps.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_product_sale //
CREATE PROCEDURE proc_validate_product_sale(
    IN p_customer_id INT,
    IN p_seller_user_id INT,
    IN p_payment_method VARCHAR(10)
)
BEGIN
    IF p_customer_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM user WHERE id = p_customer_id) THEN
        CALL proc_raise('El cliente indicado no existe.');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM user WHERE id = p_seller_user_id) THEN
        CALL proc_raise('El vendedor indicado no existe.');
    END IF;
    IF IFNULL(p_payment_method, '') NOT IN ('Cash', 'Card', 'Transfer') THEN
        CALL proc_raise('El método de pago debe ser Cash, Card o Transfer.');
    END IF;
END //

-- El total inicia en 0 y se recalcula al agregar productos (product_sale_detail)
DROP PROCEDURE IF EXISTS proc_insert_product_sale //
CREATE PROCEDURE proc_insert_product_sale(
    IN p_customer_id INT,
    IN p_seller_user_id INT,
    IN p_payment_method VARCHAR(10)
)
BEGIN
    CALL proc_validate_product_sale(p_customer_id, p_seller_user_id, p_payment_method);

    INSERT INTO product_sale (customer_id, seller_user_id, total_amount, payment_method)
    VALUES (p_customer_id, p_seller_user_id, 0, p_payment_method);
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_product_sale //
CREATE PROCEDURE proc_update_product_sale(
    IN p_id INT,
    IN p_customer_id INT,
    IN p_seller_user_id INT,
    IN p_payment_method VARCHAR(10)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM product_sale WHERE id = p_id) THEN
        CALL proc_raise('La venta indicada no existe.');
    END IF;
    CALL proc_validate_product_sale(p_customer_id, p_seller_user_id, p_payment_method);

    UPDATE product_sale
    SET customer_id = p_customer_id,
        seller_user_id = p_seller_user_id,
        payment_method = p_payment_method
    WHERE id = p_id;
END //

-- Elimina la venta y devuelve al inventario los productos vendidos
DROP PROCEDURE IF EXISTS proc_delete_product_sale //
CREATE PROCEDURE proc_delete_product_sale(
    IN p_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF NOT EXISTS (SELECT 1 FROM product_sale WHERE id = p_id) THEN
        CALL proc_raise('La venta indicada no existe.');
    END IF;

    START TRANSACTION;
    UPDATE product p
    INNER JOIN (SELECT product_id, SUM(quantity) AS qty
                FROM product_sale_detail
                WHERE product_sale_id = p_id
                GROUP BY product_id) d ON d.product_id = p.id
    SET p.stock_quantity = p.stock_quantity + d.qty;
    DELETE FROM product_sale WHERE id = p_id;
    COMMIT;
END //

-- ============================================================
-- 13. PRODUCT SALE DETAIL
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_product_sale_details //
CREATE PROCEDURE proc_select_product_sale_details(
    IN p_product_sale_id INT
)
BEGIN
    SELECT psd.id, psd.product_sale_id, psd.product_id, p.name AS product_name, psd.quantity, psd.unit_price, psd.subtotal
    FROM product_sale_detail psd
    INNER JOIN product p ON psd.product_id = p.id
    WHERE psd.product_sale_id = p_product_sale_id;
END //

DROP PROCEDURE IF EXISTS proc_select_product_sale_detail_by_id //
CREATE PROCEDURE proc_select_product_sale_detail_by_id(
    IN p_id INT
)
BEGIN
    SELECT psd.id, psd.product_sale_id, psd.product_id, p.name AS product_name, psd.quantity, psd.unit_price, psd.subtotal
    FROM product_sale_detail psd
    INNER JOIN product p ON psd.product_id = p.id
    WHERE psd.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_recalculate_sale_total //
CREATE PROCEDURE proc_recalculate_sale_total(
    IN p_product_sale_id INT
)
BEGIN
    UPDATE product_sale
    SET total_amount = (SELECT IFNULL(SUM(subtotal), 0)
                        FROM product_sale_detail
                        WHERE product_sale_id = p_product_sale_id)
    WHERE id = p_product_sale_id;
END //

-- p_unit_price NULL = precio de venta actual del producto.
-- El subtotal se calcula y el stock se descuenta automáticamente.
DROP PROCEDURE IF EXISTS proc_insert_product_sale_detail //
CREATE PROCEDURE proc_insert_product_sale_detail(
    IN p_product_sale_id INT,
    IN p_product_id INT,
    IN p_quantity INT,
    IN p_unit_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_stock INT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_new_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF NOT EXISTS (SELECT 1 FROM product_sale WHERE id = p_product_sale_id) THEN
        CALL proc_raise('La venta indicada no existe.');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product WHERE id = p_product_id) THEN
        CALL proc_raise('El producto indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM product_sale_detail
               WHERE product_sale_id = p_product_sale_id AND product_id = p_product_id) THEN
        CALL proc_raise('Ese producto ya está en la venta; modifique la cantidad del detalle existente.');
    END IF;
    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        CALL proc_raise('La cantidad debe ser mayor a 0.');
    END IF;
    IF p_unit_price IS NOT NULL AND p_unit_price < 0 THEN
        CALL proc_raise('El precio unitario no puede ser negativo.');
    END IF;

    START TRANSACTION;
    -- FOR UPDATE bloquea el producto para evitar vender el mismo stock dos veces
    SELECT stock_quantity, selling_price INTO v_stock, v_price
    FROM product WHERE id = p_product_id FOR UPDATE;
    IF v_stock < p_quantity THEN
        CALL proc_raise('Stock insuficiente para la cantidad solicitada.');
    END IF;
    SET v_price = IFNULL(p_unit_price, v_price);

    INSERT INTO product_sale_detail (product_sale_id, product_id, quantity, unit_price, subtotal)
    VALUES (p_product_sale_id, p_product_id, p_quantity, v_price, v_price * p_quantity);
    SET v_new_id = LAST_INSERT_ID();

    UPDATE product
    SET stock_quantity = stock_quantity - p_quantity
    WHERE id = p_product_id;
    CALL proc_recalculate_sale_total(p_product_sale_id);
    COMMIT;

    SELECT v_new_id AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_product_sale_detail //
CREATE PROCEDURE proc_update_product_sale_detail(
    IN p_id INT,
    IN p_quantity INT,
    IN p_unit_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_sale_id INT;
    DECLARE v_product_id INT;
    DECLARE v_old_quantity INT;
    DECLARE v_stock INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT product_sale_id, product_id, quantity INTO v_sale_id, v_product_id, v_old_quantity
    FROM product_sale_detail WHERE id = p_id;
    IF v_sale_id IS NULL THEN
        CALL proc_raise('El detalle indicado no existe.');
    END IF;
    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        CALL proc_raise('La cantidad debe ser mayor a 0.');
    END IF;
    IF p_unit_price IS NULL OR p_unit_price < 0 THEN
        CALL proc_raise('El precio unitario no puede ser negativo.');
    END IF;

    START TRANSACTION;
    SELECT stock_quantity INTO v_stock FROM product WHERE id = v_product_id FOR UPDATE;
    IF v_stock + v_old_quantity < p_quantity THEN
        CALL proc_raise('Stock insuficiente para la nueva cantidad.');
    END IF;

    UPDATE product
    SET stock_quantity = stock_quantity + v_old_quantity - p_quantity
    WHERE id = v_product_id;
    UPDATE product_sale_detail
    SET quantity = p_quantity,
        unit_price = p_unit_price,
        subtotal = p_unit_price * p_quantity
    WHERE id = p_id;
    CALL proc_recalculate_sale_total(v_sale_id);
    COMMIT;
END //

-- Elimina el detalle y devuelve la cantidad al inventario
DROP PROCEDURE IF EXISTS proc_delete_product_sale_detail //
CREATE PROCEDURE proc_delete_product_sale_detail(
    IN p_id INT
)
BEGIN
    DECLARE v_sale_id INT;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT product_sale_id, product_id, quantity INTO v_sale_id, v_product_id, v_quantity
    FROM product_sale_detail WHERE id = p_id;
    IF v_sale_id IS NULL THEN
        CALL proc_raise('El detalle indicado no existe.');
    END IF;

    START TRANSACTION;
    UPDATE product SET stock_quantity = stock_quantity + v_quantity WHERE id = v_product_id;
    DELETE FROM product_sale_detail WHERE id = p_id;
    CALL proc_recalculate_sale_total(v_sale_id);
    COMMIT;
END //

-- ============================================================
-- 14. SUPPLIER
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_suppliers //
CREATE PROCEDURE proc_select_suppliers()
BEGIN
    SELECT id, company_name, contact_name, phone, email, address
    FROM supplier
    ORDER BY company_name ASC;
END //

DROP PROCEDURE IF EXISTS proc_select_supplier_by_id //
CREATE PROCEDURE proc_select_supplier_by_id(
    IN p_id INT
)
BEGIN
    SELECT id, company_name, contact_name, phone, email, address
    FROM supplier
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_supplier //
CREATE PROCEDURE proc_validate_supplier(
    IN p_company_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100)
)
BEGIN
    IF TRIM(IFNULL(p_company_name, '')) = '' THEN
        CALL proc_raise('El nombre de la empresa es obligatorio.');
    END IF;
    IF TRIM(IFNULL(p_phone, '')) NOT REGEXP '^[0-9+() -]{7,20}$' THEN
        CALL proc_raise('El teléfono no es válido (7 a 20 dígitos).');
    END IF;
    IF TRIM(IFNULL(p_email, '')) <> '' AND TRIM(p_email) NOT REGEXP '^[^@ ]+@[^@ ]+[.][^@ ]+$' THEN
        CALL proc_raise('El correo electrónico no es válido.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_supplier //
CREATE PROCEDURE proc_insert_supplier(
    IN p_company_name VARCHAR(100),
    IN p_contact_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_address VARCHAR(150)
)
BEGIN
    CALL proc_validate_supplier(p_company_name, p_phone, p_email);

    INSERT INTO supplier (company_name, contact_name, phone, email, address)
    VALUES (TRIM(p_company_name), NULLIF(TRIM(p_contact_name), ''), TRIM(p_phone),
            NULLIF(TRIM(p_email), ''), NULLIF(TRIM(p_address), ''));
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_supplier //
CREATE PROCEDURE proc_update_supplier(
    IN p_id INT,
    IN p_company_name VARCHAR(100),
    IN p_contact_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_address VARCHAR(150)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM supplier WHERE id = p_id) THEN
        CALL proc_raise('El proveedor indicado no existe.');
    END IF;
    CALL proc_validate_supplier(p_company_name, p_phone, p_email);

    UPDATE supplier
    SET company_name = TRIM(p_company_name),
        contact_name = NULLIF(TRIM(p_contact_name), ''),
        phone = TRIM(p_phone),
        email = NULLIF(TRIM(p_email), ''),
        address = NULLIF(TRIM(p_address), '')
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_supplier //
CREATE PROCEDURE proc_delete_supplier(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM supplier WHERE id = p_id) THEN
        CALL proc_raise('El proveedor indicado no existe.');
    END IF;
    IF EXISTS (SELECT 1 FROM supplier_purchase WHERE supplier_id = p_id) THEN
        CALL proc_raise('No se puede eliminar: el proveedor tiene compras registradas.');
    END IF;

    DELETE FROM supplier WHERE id = p_id;
END //

-- ============================================================
-- 15. SUPPLIER PURCHASE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_supplier_purchases //
CREATE PROCEDURE proc_select_supplier_purchases()
BEGIN
    SELECT sp.id, sp.supplier_id, s.company_name, sp.barber_id, u.full_name AS barber_name,
           sp.barbershop_id, bs.name AS barbershop_name,
           sp.purchase_datetime, sp.tools_description, sp.total_paid
    FROM supplier_purchase sp
    INNER JOIN supplier s ON sp.supplier_id = s.id
    LEFT JOIN barber b ON sp.barber_id = b.id
    LEFT JOIN user u ON b.user_id = u.id
    LEFT JOIN barbershop bs ON sp.barbershop_id = bs.id
    ORDER BY sp.purchase_datetime DESC;
END //

DROP PROCEDURE IF EXISTS proc_select_supplier_purchase_by_id //
CREATE PROCEDURE proc_select_supplier_purchase_by_id(
    IN p_id INT
)
BEGIN
    SELECT sp.id, sp.supplier_id, s.company_name, sp.barber_id, u.full_name AS barber_name,
           sp.barbershop_id, bs.name AS barbershop_name,
           sp.purchase_datetime, sp.tools_description, sp.total_paid
    FROM supplier_purchase sp
    INNER JOIN supplier s ON sp.supplier_id = s.id
    LEFT JOIN barber b ON sp.barber_id = b.id
    LEFT JOIN user u ON b.user_id = u.id
    LEFT JOIN barbershop bs ON sp.barbershop_id = bs.id
    WHERE sp.id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_validate_supplier_purchase //
CREATE PROCEDURE proc_validate_supplier_purchase(
    IN p_supplier_id INT,
    IN p_barber_id INT,
    IN p_barbershop_id INT,
    IN p_tools_description TEXT,
    IN p_total_paid DECIMAL(10,2)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM supplier WHERE id = p_supplier_id) THEN
        CALL proc_raise('El proveedor indicado no existe.');
    END IF;
    IF p_barber_id IS NULL AND p_barbershop_id IS NULL THEN
        CALL proc_raise('La compra debe asignarse a un barbero o a una barbería.');
    END IF;
    IF p_barber_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM barber WHERE id = p_barber_id) THEN
        CALL proc_raise('El barbero indicado no existe.');
    END IF;
    IF p_barbershop_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM barbershop WHERE id = p_barbershop_id) THEN
        CALL proc_raise('La barbería indicada no existe.');
    END IF;
    IF TRIM(IFNULL(p_tools_description, '')) = '' THEN
        CALL proc_raise('La descripción de lo comprado es obligatoria.');
    END IF;
    IF p_total_paid IS NULL OR p_total_paid <= 0 THEN
        CALL proc_raise('El total pagado debe ser mayor a 0.');
    END IF;
END //

DROP PROCEDURE IF EXISTS proc_insert_supplier_purchase //
CREATE PROCEDURE proc_insert_supplier_purchase(
    IN p_supplier_id INT,
    IN p_barber_id INT,
    IN p_barbershop_id INT,
    IN p_tools_description TEXT,
    IN p_total_paid DECIMAL(10,2)
)
BEGIN
    CALL proc_validate_supplier_purchase(p_supplier_id, p_barber_id, p_barbershop_id,
                                         p_tools_description, p_total_paid);

    INSERT INTO supplier_purchase (supplier_id, barber_id, barbershop_id, tools_description, total_paid)
    VALUES (p_supplier_id, p_barber_id, p_barbershop_id, TRIM(p_tools_description), p_total_paid);
    SELECT LAST_INSERT_ID() AS id;
END //

DROP PROCEDURE IF EXISTS proc_update_supplier_purchase //
CREATE PROCEDURE proc_update_supplier_purchase(
    IN p_id INT,
    IN p_supplier_id INT,
    IN p_barber_id INT,
    IN p_barbershop_id INT,
    IN p_tools_description TEXT,
    IN p_total_paid DECIMAL(10,2)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM supplier_purchase WHERE id = p_id) THEN
        CALL proc_raise('La compra indicada no existe.');
    END IF;
    CALL proc_validate_supplier_purchase(p_supplier_id, p_barber_id, p_barbershop_id,
                                         p_tools_description, p_total_paid);

    UPDATE supplier_purchase
    SET supplier_id = p_supplier_id,
        barber_id = p_barber_id,
        barbershop_id = p_barbershop_id,
        tools_description = TRIM(p_tools_description),
        total_paid = p_total_paid
    WHERE id = p_id;
END //

DROP PROCEDURE IF EXISTS proc_delete_supplier_purchase //
CREATE PROCEDURE proc_delete_supplier_purchase(
    IN p_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM supplier_purchase WHERE id = p_id) THEN
        CALL proc_raise('La compra indicada no existe.');
    END IF;

    DELETE FROM supplier_purchase WHERE id = p_id;
END //

DELIMITER ;
