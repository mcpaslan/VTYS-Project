"""add birth_date to user

Revision ID: db1c2f380eb7
Revises: dd022327ec47
Create Date: 2025-12-10 20:37:55.240950

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "db1c2f380eb7"
down_revision: Union[str, Sequence[str], None] = "dd022327ec47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        ALTER TABLE users ADD COLUMN birth_date DATE NOT NULL;
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE users DROP COLUMN birth_date;
    """
    )
