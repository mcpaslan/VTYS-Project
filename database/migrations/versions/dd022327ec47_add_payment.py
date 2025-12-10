"""add payment

Revision ID: dd022327ec47
Revises: a5ea6ffb0e3f
Create Date: 2025-12-10 20:32:13.904579

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dd022327ec47"
down_revision: Union[str, Sequence[str], None] = "a5ea6ffb0e3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
       CREATE TABLE payment_types (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );
       ALTER TABLE subscriptions ADD COLUMN payment_type_id INT NOT NULL REFERENCES payment_types(id);
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE subscriptions DROP COLUMN payment_type_id;
        DROP TABLE payment_types;
    """
    )
