"""create users table

Revision ID: a5ea6ffb0e3f
Revises:
Create Date: 2025-11-30 16:19:01.829697

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a5ea6ffb0e3f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE TYPE gender_enum AS ENUM ('Erkek', 'Kadın', 'Diğer');
        CREATE TYPE status_enum AS ENUM ('Aktif', 'Pasif');

        CREATE TABLE packages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            duration_days INT NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            gender gender_enum NOT NULL,
            tc_number VARCHAR(11) NOT NULL UNIQUE,
            status status_enum NOT NULL DEFAULT 'Aktif',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE subscriptions (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users(id),
            package_id INT NOT NULL REFERENCES packages(id),
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            price_sold DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE coaches (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )


def downgrade():

    op.execute(
        """
        DROP TABLE subscriptions;
        DROP TABLE users;
        DROP TABLE coaches;
        DROP TABLE packages;
        DROP TYPE gender_enum;
        DROP TYPE status_enum;
    """
    )
