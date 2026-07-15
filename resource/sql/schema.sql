-- :name create_users_table :affected
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    email VARCHAR
);

-- :name insert_user :affected
INSERT INTO
    users (id, name, email)
VALUES
    (:id, :name, :email);

-- :name get_all_users :many
SELECT
    *
FROM
    users;