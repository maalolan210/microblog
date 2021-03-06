"""add path

Revision ID: ecdbb5c71ee7
Revises: 0ec6f57d2eab
Create Date: 2021-12-08 21:47:52.896437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecdbb5c71ee7'
down_revision = '0ec6f57d2eab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('path', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'path')
    # ### end Alembic commands ###
