"""add programs

Revision ID: 5f2e3c6d2cb6
Revises: db1c2f380eb7
Create Date: 2025-12-10 20:39:18.603567

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f2e3c6d2cb6"
down_revision: Union[str, Sequence[str], None] = "db1c2f380eb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE TABLE exercises (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE programs (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description TEXT NOT NULL
        );
        CREATE TABLE program_exercises (
            id SERIAL PRIMARY KEY,
            program_id INT NOT NULL REFERENCES programs(id),
            exercise_id INT NOT NULL REFERENCES exercises(id),
            sets INT NOT NULL,
            reps INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )


def downgrade():
    op.execute(
        """
        DROP TABLE program_exercises;
        DROP TABLE programs;
        DROP TABLE exercises;
    """
    )
