CREATE DATABASE hotel_management;
USE hotel_management;
Create table customers ( customer_id INT AUTO_INCREMENT PRIMARY KEY,
 first_name VARCHAR(50) NOT NULL,
 last_name VARCHAR(50),
 gender VARCHAR(20),
 age INT,
 city VARCHAR(50),
 state VARCHAR(50),
 country VARCHAR(50),
 nationality VARCHAR(50),
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
 
 CREATE TABLE rooms (
 room_id INT AUTO_INCREMENT PRIMARY KEY,
 room_number VARCHAR(10) UNIQUE NOT NULL,
 room_type VARCHAR(30) NOT NULL,
 price_per_night DECIMAL(10,2) NOT NULL,
 capacity INT NOT NULL,
 room_status VARCHAR(30) DEFAULT "Available");
 
 CREATE TABLE bookings(
 booking_id INT AUTO_INCREMENT PRIMARY KEY,
 customer_id INT NOT NULL,
 room_id INT NOT NULL,
 booking_date DATE NOT NULL,
 check_in DATE NOT NULL,
 check_out DATE NOT NULL,
 adults INT NOT NULL,
 children INT DEFAULT 0,
 booking_source VARCHAR(30),
 booking_status VARCHAR(30) DEFAULT "Confirmed",
 FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
 FOREIGN KEY (room_id) REFERENCES rooms(room_id));
 
 CREATE TABLE bills (
 bill_id INT AUTO_INCREMENT PRIMARY KEY,
 booking_id INT NOT NULL,
 rooms_charges DECIMAL(10.2) DEFAULT 0,
 food_charges DECIMAL(10,2) DEFAULT 0,
 services_charges DECIMAL(10,2) DEFAULT 0,
 discount DECIMAL(10,2) DEFAULT 0,
 
 
 