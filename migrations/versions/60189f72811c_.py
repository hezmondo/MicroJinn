"""empty message

Revision ID: 60189f72811c
Revises: a6bf51a4473d
Create Date: 2018-12-23 17:17:06.201116

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '60189f72811c'
down_revision = 'a6bf51a4473d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('income', 'typebankacc_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('income', 'typepayment_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_foreign_key(None, 'income', 'typepayment', ['typepayment_id'], ['id'])
    op.create_foreign_key(None, 'income', 'typebankacc', ['typebankacc_id'], ['id'])
    op.alter_column('incomealloc', 'alloc_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_foreign_key(None, 'incomealloc', 'chargetype', ['chargetype_id'], ['id'])
    op.create_foreign_key(None, 'incomealloc', 'income', ['income_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'incomealloc', type_='foreignkey')
    op.drop_constraint(None, 'incomealloc', type_='foreignkey')
    op.alter_column('incomealloc', 'alloc_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_constraint(None, 'income', type_='foreignkey')
    op.drop_constraint(None, 'income', type_='foreignkey')
    op.alter_column('income', 'typepayment_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('income', 'typebankacc_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###
