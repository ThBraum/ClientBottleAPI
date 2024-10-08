"""new functions

Revision ID: 933fc3a811b3
Revises: f5058c00fe1a
Create Date: 2024-08-18 02:22:33.611711

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "933fc3a811b3"
down_revision: Union[str, None] = "f5058c00fe1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS unaccent SCHEMA public;

        CREATE OR REPLACE FUNCTION normalize_product_name(name TEXT) RETURNS TEXT AS
        $$
        BEGIN
            IF name IS NULL THEN
                RETURN NULL;
            ELSE
                RETURN public.unaccent(LOWER(name));
            END IF;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE
                        PARALLEL SAFE;

        CREATE OR REPLACE FUNCTION try_cast_to_int(value TEXT)
            RETURNS BIGINT AS
        $$
        BEGIN
            BEGIN
                RETURN value::BIGINT;
            EXCEPTION
                WHEN OTHERS THEN
                    RETURN NULL;
            END;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE
                        PARALLEL SAFE;
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        """
        DROP FUNCTION try_cast_to_int;
        DROP FUNCTION normalize_product_name;

        DROP EXTENSION unaccent;
        """
    )
    # ### end Alembic commands ###
