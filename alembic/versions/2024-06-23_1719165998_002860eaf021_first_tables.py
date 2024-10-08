"""First tables

Revision ID: 002860eaf021
Revises: 70768ce0faa5
Create Date: 2024-06-23 18:06:38.139523

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002860eaf021"
down_revision: Union[str, None] = "70768ce0faa5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id_user", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("api_key", sa.String(), nullable=True),
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
            ["creation_user_id"], ["user.id_user"], name=op.f("fk_user_creation_user_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["update_user_id"], ["user.id_user"], name=op.f("fk_user_update_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id_user", name=op.f("pk_user")),
        sa.UniqueConstraint("email", name=op.f("uq_user_email")),
        sa.UniqueConstraint("username", name=op.f("uq_user_username")),
    )
    op.create_index(op.f("ix_user_creation_user_id"), "user", ["creation_user_id"], unique=False)
    op.create_index(op.f("ix_user_update_user_id"), "user", ["update_user_id"], unique=False)
    op.create_table(
        "bottle_brand",
        sa.Column("id_bottle_brand", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
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
            name=op.f("fk_bottle_brand_creation_user_id_user"),
        ),
        sa.ForeignKeyConstraint(
            ["update_user_id"], ["user.id_user"], name=op.f("fk_bottle_brand_update_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id_bottle_brand", name=op.f("pk_bottle_brand")),
        sa.UniqueConstraint("name", name=op.f("uq_bottle_brand_name")),
    )
    op.create_index(
        op.f("ix_bottle_brand_creation_user_id"),
        "bottle_brand",
        ["creation_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_bottle_brand_update_user_id"), "bottle_brand", ["update_user_id"], unique=False
    )
    op.create_table(
        "client",
        sa.Column("id_client", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
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
            ["creation_user_id"], ["user.id_user"], name=op.f("fk_client_creation_user_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["update_user_id"], ["user.id_user"], name=op.f("fk_client_update_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id_client", name=op.f("pk_client")),
    )
    op.create_index(
        op.f("ix_client_creation_user_id"), "client", ["creation_user_id"], unique=False
    )
    op.create_index(op.f("ix_client_update_user_id"), "client", ["update_user_id"], unique=False)
    op.create_table(
        "bottle",
        sa.Column("id_bottle", sa.Integer(), nullable=False),
        sa.Column("id_bottle_brand", sa.Integer(), nullable=False),
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
            ["creation_user_id"], ["user.id_user"], name=op.f("fk_bottle_creation_user_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["id_bottle_brand"],
            ["bottle_brand.id_bottle_brand"],
            name=op.f("fk_bottle_id_bottle_brand_bottle_brand"),
        ),
        sa.ForeignKeyConstraint(
            ["update_user_id"], ["user.id_user"], name=op.f("fk_bottle_update_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id_bottle", name=op.f("pk_bottle")),
    )
    op.create_index(
        op.f("ix_bottle_creation_user_id"), "bottle", ["creation_user_id"], unique=False
    )
    op.create_index(op.f("ix_bottle_update_user_id"), "bottle", ["update_user_id"], unique=False)
    op.create_table(
        "client_bottle_transaction",
        sa.Column("id_client_bottle_transaction", sa.Integer(), nullable=False),
        sa.Column("id_client", sa.Integer(), nullable=False),
        sa.Column("id_bottle", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("current_timestamp_brazil()"),
            nullable=False,
        ),
        sa.Column("recorded_by", sa.String(), nullable=True),
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
            name=op.f("fk_client_bottle_transaction_creation_user_id_user"),
        ),
        sa.ForeignKeyConstraint(
            ["id_bottle"],
            ["bottle.id_bottle"],
            name=op.f("fk_client_bottle_transaction_id_bottle_bottle"),
        ),
        sa.ForeignKeyConstraint(
            ["id_client"],
            ["client.id_client"],
            name=op.f("fk_client_bottle_transaction_id_client_client"),
        ),
        sa.ForeignKeyConstraint(
            ["update_user_id"],
            ["user.id_user"],
            name=op.f("fk_client_bottle_transaction_update_user_id_user"),
        ),
        sa.PrimaryKeyConstraint(
            "id_client_bottle_transaction", name=op.f("pk_client_bottle_transaction")
        ),
    )
    op.create_index(
        "ClientBotteTransaction_UNIQUE",
        "client_bottle_transaction",
        ["id_client", "id_bottle", "fl_active"],
        unique=True,
    )
    op.create_index(
        op.f("ix_client_bottle_transaction_creation_user_id"),
        "client_bottle_transaction",
        ["creation_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_client_bottle_transaction_update_user_id"),
        "client_bottle_transaction",
        ["update_user_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_client_bottle_transaction_update_user_id"), table_name="client_bottle_transaction"
    )
    op.drop_index(
        op.f("ix_client_bottle_transaction_creation_user_id"),
        table_name="client_bottle_transaction",
    )
    op.drop_index("ClientBotteTransaction_UNIQUE", table_name="client_bottle_transaction")
    op.drop_table("client_bottle_transaction")
    op.drop_index(op.f("ix_bottle_update_user_id"), table_name="bottle")
    op.drop_index(op.f("ix_bottle_creation_user_id"), table_name="bottle")
    op.drop_table("bottle")
    op.drop_index(op.f("ix_client_update_user_id"), table_name="client")
    op.drop_index(op.f("ix_client_creation_user_id"), table_name="client")
    op.drop_table("client")
    op.drop_index(op.f("ix_bottle_brand_update_user_id"), table_name="bottle_brand")
    op.drop_index(op.f("ix_bottle_brand_creation_user_id"), table_name="bottle_brand")
    op.drop_table("bottle_brand")
    op.drop_index(op.f("ix_user_update_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_creation_user_id"), table_name="user")
    op.drop_table("user")
    # ### end Alembic commands ###
