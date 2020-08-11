"""update roles

Revision ID: 3fc54b5097d1
Revises: d40ed63134e7
Create Date: 2020-08-06 07:55:43.740321

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3fc54b5097d1'
down_revision = 'd40ed63134e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('User')
    op.drop_table('Role')
    op.add_column('roles', sa.Column('default', sa.Boolean(), nullable=True))
    op.add_column('roles', sa.Column('permissions', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_column('roles', 'permissions')
    op.drop_column('roles', 'default')
    op.create_table('Role',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('User',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('role_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], name='User_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
