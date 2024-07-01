"""Create functions

Revision ID: 70768ce0faa5
Revises:
Create Date: 2024-06-23 02:57:06.515447

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "70768ce0faa5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION current_timestamp_brazil() RETURNS TIMESTAMP WITH TIME ZONE AS $$
        BEGIN
            RETURN CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo';
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION current_timestamp_brazil;")
