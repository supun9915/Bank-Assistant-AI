# Database Migrations

A lightweight migration system similar to Prisma Migrate / Flyway.  
Migration files live in the `migrations/` folder and are tracked in a `_migrations` table so each file runs **exactly once**.

---

## Commands

| Command                           | Description                        |
| --------------------------------- | ---------------------------------- |
| `python migrate.py up`            | Apply all pending migrations       |
| `python migrate.py status`        | Show applied vs pending migrations |
| `python migrate.py create <name>` | Scaffold a new migration file      |

---

## Quick Start

### 1. Apply all migrations

```bash
python migrate.py up
```

### 2. Check migration status

```bash
python migrate.py status
```

Output example:

```
Ver    Status     File
------------------------------------------------------------
  V001  Applied    V001__initial_schema.sql
  V002  Pending    V002__add_phone_to_users.sql

2 migration(s) total — 1 applied, 1 pending
```

### 3. Create a new migration

```bash
python migrate.py create add phone to users
```

This generates:

```
migrations/V002__add_phone_to_users.sql
```

Open the file and write your SQL, then run `python migrate.py up`.

---

## File Naming Convention

```
V<version>__<description>.sql
```

| Part            | Example              | Notes                                |
| --------------- | -------------------- | ------------------------------------ |
| `V<version>`    | `V001`, `V002`       | Auto-incremented by `create` command |
| `__`            | —                    | Double underscore separator          |
| `<description>` | `add_phone_to_users` | Words separated by underscores       |

---

## Example Migrations

### Add a column

```sql
-- migrations/V002__add_phone_to_users.sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

### Create a new table

```sql
-- migrations/V003__create_loans_table.sql
CREATE TABLE loans (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT NOT NULL,
    amount     DECIMAL(15, 2) NOT NULL,
    status     ENUM('active', 'paid', 'defaulted') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Insert seed / reference data

```sql
-- migrations/V004__seed_loan_types.sql
INSERT IGNORE INTO loan_types (name) VALUES ('personal'), ('mortgage'), ('auto');
```

---

## How It Works

1. On first run, a `_migrations` table is created in the database.
2. `migrate.py up` reads all `V*.sql` files in version order.
3. Any version not yet recorded in `_migrations` is executed and marked as applied.
4. Already-applied migrations are **never run again**.

---

## Environment Variables

The migration tool reads the same `.env` as the main app:

| Variable      | Default           | Description     |
| ------------- | ----------------- | --------------- |
| `DB_HOST`     | `localhost`       | MySQL host      |
| `DB_PORT`     | `3306`            | MySQL port      |
| `DB_USER`     | `root`            | MySQL user      |
| `DB_PASSWORD` | `mysql`           | MySQL password  |
| `DB_NAME`     | `banking_chatbot` | Target database |
