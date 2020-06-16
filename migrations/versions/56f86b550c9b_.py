"""empty message

Revision ID: 56f86b550c9b
Revises: c30a3dd0b72b
Create Date: 2020-06-12 18:18:04.232284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56f86b550c9b'
down_revision = 'c30a3dd0b72b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_talent')
    # ### end Alembic commands ###