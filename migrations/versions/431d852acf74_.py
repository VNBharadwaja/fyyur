"""empty message

Revision ID: 431d852acf74
Revises: 69029d7f8ce3
Create Date: 2020-06-11 20:04:03.213481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '431d852acf74'
down_revision = '69029d7f8ce3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('past_shows', sa.ARRAY(sa.Integer()), nullable=True, foreign_keys='Artist.id'))
    op.add_column('Venue', sa.Column('upcoming_shows', sa.ARRAY(sa.Integer()), nullable=True, foreign_keys='Artist.id'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'upcoming_shows')
    op.drop_column('Venue', 'past_shows')
    # ### end Alembic commands ###
