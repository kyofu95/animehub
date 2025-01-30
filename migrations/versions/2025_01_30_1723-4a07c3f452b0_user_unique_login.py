"""user unique login

Revision ID: 4a07c3f452b0
Revises: 1c27cafc5859
Create Date: 2025-01-30 17:23:15.011118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a07c3f452b0'
down_revision: Union[str, None] = '1c27cafc5859'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq_user_login'), 'user', ['login'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_user_login'), 'user', type_='unique')
    # ### end Alembic commands ###
