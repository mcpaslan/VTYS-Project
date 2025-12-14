"""Fixed program delete problem

Revision ID: efcfca4bfcfa
Revises: 53c92ba97937
Create Date: 2025-12-14 14:50:43.022962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efcfca4bfcfa'
down_revision: Union[str, Sequence[str], None] = '53c92ba97937'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        ALTER TABLE program_exercises
            DROP CONSTRAINT program_exercises_program_id_fkey;
        ALTER TABLE program_exercises
            ADD CONSTRAINT program_exercises_program_id_fkey
            FOREIGN KEY (program_id)
            REFERENCES programs (id)
            ON DELETE CASCADE;

    
    """
    )


def downgrade():
    op.execute(
        """
        # Geri alma SQL komutlarınızı buraya yazın
    """
    )