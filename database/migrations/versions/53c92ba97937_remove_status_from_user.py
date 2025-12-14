"""remove status from user

Revision ID: 53c92ba97937
Revises: 51932dfbbaa2
Create Date: 2025-12-14 14:27:02.295008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53c92ba97937'
down_revision: Union[str, Sequence[str], None] = '51932dfbbaa2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
             '''ALTER TABLE subscriptions
            DROP CONSTRAINT subscriptions_user_id_fkey;

            -- 2. CASCADE kuralı ile yeniden ekle
            ALTER TABLE subscriptions
            ADD CONSTRAINT subscriptions_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES users (id)
            ON DELETE CASCADE;'''
    )


def downgrade():
    op.execute(
        """
        -- 1. CASCADE kısıtlamasını kaldır
            ALTER TABLE subscriptions
            DROP CONSTRAINT subscriptions_user_id_fkey

            -- 2. Kısıtlamayı varsayılan (RESTRICT / NO ACTION) kuralı ile geri ekle
            -- ON DELETE kuralı belirtilmediğinde PostgreSQL/SQL varsayılan kısıtlayıcı kuralı kullanır.
            ALTER TABLE subscriptions
            ADD CONSTRAINT subscriptions_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES users (id);
    """
    )