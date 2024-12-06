-- Use the Railway-provided database
USE railway;

-- Create `users` table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL
);

-- Create `orders` table if it doesn't exist
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    juice_name VARCHAR(100),
    cup_size VARCHAR(10),
    fruits TEXT,
    toppings TEXT,
    total_calories INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create `juices` table if it doesn't exist
CREATE TABLE IF NOT EXISTS juices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    base_calories INT,
    fat FLOAT DEFAULT 0,
    cholesterol FLOAT DEFAULT 0,
    sodium FLOAT DEFAULT 0,
    carbohydrates FLOAT DEFAULT 0,
    fiber FLOAT DEFAULT 0,
    sugars FLOAT DEFAULT 0,
    protein FLOAT DEFAULT 0
);

-- Create `fruits` table if it doesn't exist
CREATE TABLE IF NOT EXISTS fruits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    calories_per_gram INT,
    fat FLOAT DEFAULT 0,
    cholesterol FLOAT DEFAULT 0,
    sodium FLOAT DEFAULT 0,
    carbohydrates FLOAT DEFAULT 0,
    fiber FLOAT DEFAULT 0,
    sugars FLOAT DEFAULT 0,
    protein FLOAT DEFAULT 0
);

-- Create `toppings` table if it doesn't exist
CREATE TABLE IF NOT EXISTS toppings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    calories_per_gram INT,
    fat FLOAT DEFAULT 0,
    cholesterol FLOAT DEFAULT 0,
    sodium FLOAT DEFAULT 0,
    carbohydrates FLOAT DEFAULT 0,
    fiber FLOAT DEFAULT 0,
    sugars FLOAT DEFAULT 0,
    protein FLOAT DEFAULT 0
);

-- Insert data into `juices` table using `INSERT IGNORE`
INSERT IGNORE INTO juices (name, base_calories, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein)
VALUES
    ('Apple Juice', 50, 0, 0, 5, 14, 0, 12, 0.5),
    ('Orange Juice', 60, 0, 0, 1, 16, 0.5, 15, 1),
    ('Mango Juice', 70, 0, 0, 3, 18, 1, 17, 0.7),
    ('Pineapple Juice', 65, 0, 0, 2, 15, 0.4, 14, 0.6),
    ('Grape Juice', 55, 0, 0, 4, 13, 0.3, 11, 0.4),
    ('Strawberry Juice', 75, 0, 0, 1, 19, 0.8, 18, 0.9),
    ('Watermelon Juice', 40, 0, 0, 1, 10, 0.2, 9, 0.2),
    ('Pomegranate Juice', 80, 0, 0, 3, 20, 0.7, 19, 0.8),
    ('Lemon Juice', 30, 0, 0, 2, 8, 0.3, 6, 0.4),
    ('Kiwi Juice', 45, 0, 0, 3, 11, 0.4, 10, 0.6);

-- Insert data into `fruits` table using `INSERT IGNORE`
INSERT IGNORE INTO fruits (name, calories_per_gram, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein)
VALUES
    ('Apple', 0.52, 0.1, 0, 1, 14, 2.4, 10, 0.3),
    ('Banana', 0.96, 0.3, 0, 1, 27, 3.1, 14, 1.3),
    ('Grape', 0.69, 0.2, 0, 2, 17, 1.0, 16, 0.6),
    ('Mango', 0.60, 0.2, 0, 1, 15, 1.6, 14, 0.8),
    ('Strawberry', 0.32, 0.1, 0, 1, 8, 1.8, 6, 0.4),
    ('Watermelon', 0.30, 0.1, 0, 1, 8, 0.6, 6, 0.2),
    ('Pineapple', 0.50, 0.1, 0, 2, 13, 1.4, 10, 0.5),
    ('Pomegranate', 0.83, 0.3, 0, 3, 19, 3.4, 14, 1.7),
    ('Kiwi', 0.61, 0.2, 0, 2, 15, 2.1, 13, 0.9),
    ('Orange', 0.47, 0.1, 0, 1, 12, 2.0, 9, 0.7);

-- Insert data into `toppings` table using `INSERT IGNORE`
INSERT IGNORE INTO toppings (name, calories_per_gram, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein)
VALUES
    ('Whipped Cream', 2, 0.2, 1, 5, 0.3, 0, 0.3, 0.1),
    ('Honey', 4, 0, 0, 2, 1, 0, 1, 0),
    ('Chia Seeds', 4.9, 0.3, 0, 1, 1.5, 0.4, 0.5, 0.2),
    ('Crushed Nuts', 6, 0.5, 0, 3, 2, 0.1, 2, 0.3),
    ('Chocolate Syrup', 7, 0.5, 0, 1, 3, 0.2, 3, 0.2),
    ('Coconut Flakes', 5, 0.4, 0, 2, 1.2, 0.3, 1, 0.1),
    ('Granola', 5.5, 0.6, 0, 3, 3, 0.5, 2, 0.4),
    ('Mint Leaves', 0.2, 0, 0, 0, 0.5, 0.2, 0, 0.1),
    ('Cinnamon', 1.2, 0, 0, 1, 0.4, 0.1, 0.1, 0.1),
    ('No Toppings', 0, 0, 0, 0, 0, 0, 0, 0);
