"""update client table

Revision ID: 53a70f304619
Revises: a5b3d34b5fde
Create Date: 2024-09-23 09:43:49.793351

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "53a70f304619"
down_revision: Union[str, None] = "a5b3d34b5fde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("client", sa.Column("last_name", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("client", "last_name")
    # ### end Alembic commands ###
