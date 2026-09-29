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

DELIMITER //

-- ============================================================
-- 1. ROLE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_roles //
CREATE PROCEDURE proc_select_roles()
BEGIN
    SELECT id, name FROM role ORDER BY id ASC;
END //

DROP PROCEDURE IF EXISTS proc_insert_role //
CREATE PROCEDURE proc_insert_role(
    IN p_name VARCHAR(50)
)
BEGIN
    INSERT INTO role (name) VALUES (p_name);
END //

-- ============================================================
-- 2. USER
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_users //
CREATE PROCEDURE proc_select_users()
BEGIN
    SELECT u.id, u.role_id, r.name AS role_name, u.full_name, u.email, u.phone, u.created_at
    FROM user u
    INNER JOIN role r ON u.role_id = r.id;
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
    INSERT INTO user (role_id, full_name, email, password_hash, phone)
    VALUES (p_role_id, p_full_name, p_email, p_password_hash, p_phone);
END //

-- ============================================================
-- 3. BARBERSHOP
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_barbershops //
CREATE PROCEDURE proc_select_barbershops()
BEGIN
    SELECT b.id, b.manager_id, u.full_name AS manager_name, b.name, b.address, b.city, b.phone
    FROM barbershop b
    INNER JOIN user u ON b.manager_id = u.id;
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
    INSERT INTO barbershop (manager_id, name, address, city, phone)
    VALUES (p_manager_id, p_name, p_address, p_city, p_phone);
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
    LEFT JOIN barbershop bs ON b.barbershop_id = bs.id;
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
    INSERT INTO barber (user_id, barbershop_id, provides_home_service, provides_shop_service, commission_rate)
    VALUES (p_user_id, p_barbershop_id, p_provides_home_service, p_provides_shop_service, p_commission_rate);
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
    WHERE barber_id = p_barber_id;
END //

DROP PROCEDURE IF EXISTS proc_insert_barber_schedule //
CREATE PROCEDURE proc_insert_barber_schedule(
    IN p_barber_id INT,
    IN p_day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_lunch_start_time TIME,
    IN p_lunch_end_time TIME
)
BEGIN
    INSERT INTO barber_schedule (barber_id, day_of_week, start_time, end_time, lunch_start_time, lunch_end_time)
    VALUES (p_barber_id, p_day_of_week, p_start_time, p_end_time, p_lunch_start_time, p_lunch_end_time);
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
    WHERE barber_id = p_barber_id;
END //

DROP PROCEDURE IF EXISTS proc_insert_schedule_block //
CREATE PROCEDURE proc_insert_schedule_block(
    IN p_barber_id INT,
    IN p_start_datetime DATETIME,
    IN p_end_datetime DATETIME,
    IN p_reason VARCHAR(255)
)
BEGIN
    INSERT INTO schedule_block (barber_id, start_datetime, end_datetime, reason)
    VALUES (p_barber_id, p_start_datetime, p_end_datetime, p_reason);
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

DROP PROCEDURE IF EXISTS proc_insert_service //
CREATE PROCEDURE proc_insert_service(
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_base_price DECIMAL(10,2),
    IN p_duration_minutes INT,
    IN p_buffer_minutes INT
)
BEGIN
    INSERT INTO service (name, description, base_price, duration_minutes, buffer_minutes)
    VALUES (p_name, p_description, p_base_price, p_duration_minutes, p_buffer_minutes);
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
           COALESCE(bs.custom_price, s.base_price) AS final_price,
           COALESCE(bs.custom_duration_minutes, s.duration_minutes) AS final_duration
    FROM barber_service bs
    INNER JOIN service s ON bs.service_id = s.id
    WHERE bs.barber_id = p_barber_id;
END //

DROP PROCEDURE IF EXISTS proc_insert_barber_service //
CREATE PROCEDURE proc_insert_barber_service(
    IN p_barber_id INT,
    IN p_service_id INT,
    IN p_custom_price DECIMAL(10,2),
    IN p_custom_duration_minutes INT
)
BEGIN
    INSERT INTO barber_service (barber_id, service_id, custom_price, custom_duration_minutes)
    VALUES (p_barber_id, p_service_id, p_custom_price, p_custom_duration_minutes);
END //

-- ============================================================
-- 9. APPOINTMENT
-- ============================================================

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

DROP PROCEDURE IF EXISTS proc_insert_appointment //
CREATE PROCEDURE proc_insert_appointment(
    IN p_customer_id INT,
    IN p_barber_id INT,
    IN p_barbershop_id INT,
    IN p_appointment_date DATE,
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_location_type ENUM('Shop', 'Home'),
    IN p_home_address VARCHAR(200),
    IN p_total_amount DECIMAL(10,2)
)
BEGIN
    INSERT INTO appointment (customer_id, barber_id, barbershop_id, appointment_date, start_time, end_time, location_type, home_address, total_amount)
    VALUES (p_customer_id, p_barber_id, p_barbershop_id, p_appointment_date, p_start_time, p_end_time, p_location_type, p_home_address, p_total_amount);
END //

DROP PROCEDURE IF EXISTS proc_update_appointment_status //
CREATE PROCEDURE proc_update_appointment_status(
    IN p_appointment_id INT,
    IN p_new_status ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled')
)
BEGIN
    UPDATE appointment
    SET status = p_new_status
    WHERE id = p_appointment_id;
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

DROP PROCEDURE IF EXISTS proc_insert_appointment_detail //
CREATE PROCEDURE proc_insert_appointment_detail(
    IN p_appointment_id INT,
    IN p_service_id INT,
    IN p_applied_price DECIMAL(10,2),
    IN p_applied_duration_minutes INT
)
BEGIN
    INSERT INTO appointment_service_detail (appointment_id, service_id, applied_price, applied_duration_minutes)
    VALUES (p_appointment_id, p_service_id, p_applied_price, p_applied_duration_minutes);
END //

-- ============================================================
-- 11. PRODUCT
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_products //
CREATE PROCEDURE proc_select_products()
BEGIN
    SELECT id, barbershop_id, barber_id, name, description, selling_price, stock_quantity, min_stock_level
    FROM product
    WHERE stock_quantity > 0;
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
    INSERT INTO product (barbershop_id, barber_id, name, description, selling_price, stock_quantity, min_stock_level)
    VALUES (p_barbershop_id, p_barber_id, p_name, p_description, p_selling_price, p_stock_quantity, p_min_stock_level);
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

DROP PROCEDURE IF EXISTS proc_insert_product_sale //
CREATE PROCEDURE proc_insert_product_sale(
    IN p_customer_id INT,
    IN p_seller_user_id INT,
    IN p_total_amount DECIMAL(10,2),
    IN p_payment_method ENUM('Cash', 'Card', 'Transfer')
)
BEGIN
    INSERT INTO product_sale (customer_id, seller_user_id, total_amount, payment_method)
    VALUES (p_customer_id, p_seller_user_id, p_total_amount, p_payment_method);
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

DROP PROCEDURE IF EXISTS proc_insert_product_sale_detail //
CREATE PROCEDURE proc_insert_product_sale_detail(
    IN p_product_sale_id INT,
    IN p_product_id INT,
    IN p_quantity INT,
    IN p_unit_price DECIMAL(10,2),
    IN p_subtotal DECIMAL(10,2)
)
BEGIN
    INSERT INTO product_sale_detail (product_sale_id, product_id, quantity, unit_price, subtotal)
    VALUES (p_product_sale_id, p_product_id, p_quantity, p_unit_price, p_subtotal);
    
    -- Actualizar inventario de productos automáticamente
    UPDATE product
    SET stock_quantity = stock_quantity - p_quantity
    WHERE id = p_product_id;
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

DROP PROCEDURE IF EXISTS proc_insert_supplier //
CREATE PROCEDURE proc_insert_supplier(
    IN p_company_name VARCHAR(100),
    IN p_contact_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_address VARCHAR(150)
)
BEGIN
    INSERT INTO supplier (company_name, contact_name, phone, email, address)
    VALUES (p_company_name, p_contact_name, p_phone, p_email, p_address);
END //

-- ============================================================
-- 15. SUPPLIER PURCHASE
-- ============================================================

DROP PROCEDURE IF EXISTS proc_select_supplier_purchases //
CREATE PROCEDURE proc_select_supplier_purchases()
BEGIN
    SELECT sp.id, sp.supplier_id, s.company_name, sp.barber_id, sp.barbershop_id,
           sp.purchase_datetime, sp.tools_description, sp.total_paid
    FROM supplier_purchase sp
    INNER JOIN supplier s ON sp.supplier_id = s.id
    ORDER BY sp.purchase_datetime DESC;
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
    INSERT INTO supplier_purchase (supplier_id, barber_id, barbershop_id, tools_description, total_paid)
    VALUES (p_supplier_id, p_barber_id, p_barbershop_id, p_tools_description, p_total_paid);
END //

DELIMITER ;