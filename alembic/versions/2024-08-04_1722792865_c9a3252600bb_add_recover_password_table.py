"""add recover_password table

Revision ID: c9a3252600bb
Revises: 9e41d799f14a
Create Date: 2024-08-04 17:34:25.305667

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9a3252600bb"
down_revision: Union[str, None] = "9e41d799f14a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "recover_password",
        sa.Column("id_recover_password", sa.Integer(), nullable=False),
        sa.Column("id_user", sa.Integer(), nullable=False),
        sa.Column("token", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("fl_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("current_timestamp_brazil()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("creation_user_id", sa.Integer(), server_default="1", nullable=False),
        sa.Column("update_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["creation_user_id"],
            ["user.id_user"],
            name=op.f("fk_recover_password_creation_user_id_user"),
        ),
        sa.ForeignKeyConstraint(
            ["id_user"], ["user.id_user"], name=op.f("fk_recover_password_id_user_user")
        ),
        sa.ForeignKeyConstraint(
            ["update_user_id"],
            ["user.id_user"],
            name=op.f("fk_recover_password_update_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id_recover_password", name=op.f("pk_recover_password")),
        sa.UniqueConstraint("email", name=op.f("uq_recover_password_email")),
    )
    op.create_index(
        op.f("ix_recover_password_creation_user_id"),
        "recover_password",
        ["creation_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recover_password_id_user"), "recover_password", ["id_user"], unique=False
    )
    op.create_index(op.f("ix_recover_password_token"), "recover_password", ["token"], unique=True)
    op.create_index(
        op.f("ix_recover_password_update_user_id"),
        "recover_password",
        ["update_user_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_recover_password_update_user_id"), table_name="recover_password")
    op.drop_index(op.f("ix_recover_password_token"), table_name="recover_password")
    op.drop_index(op.f("ix_recover_password_id_user"), table_name="recover_password")
    op.drop_index(op.f("ix_recover_password_creation_user_id"), table_name="recover_password")
    op.drop_table("recover_password")
    # ### end Alembic commands ###
