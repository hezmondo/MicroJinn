"""empty message

Revision ID: 8d4257c7a02a
Revises: d277e38015b5
Create Date: 2018-11-30 18:36:57.622009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d4257c7a02a'
down_revision = 'd277e38015b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('property',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('proptype', sa.String(length=1), nullable=True),
    sa.Column('propaddr', sa.String(length=180), nullable=True),
    sa.Column('rentcode', sa.String(length=10), nullable=True),
    sa.Column('rent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rent_id'], ['rent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('property')
    # ### end Alembic commands ###
