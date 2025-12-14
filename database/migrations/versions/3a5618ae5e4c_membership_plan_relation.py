"""membership plan relation

Revision ID: 3a5618ae5e4c
Revises: efcfca4bfcfa
Create Date: 2025-12-14 22:41:00.640326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a5618ae5e4c'
down_revision: Union[str, Sequence[str], None] = 'efcfca4bfcfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        # SQL komutlarınızı buraya yazın
    """
    )


def downgrade():
    op.execute(
        """
        # Geri alma SQL komutlarınızı buraya yazın
    """
    )