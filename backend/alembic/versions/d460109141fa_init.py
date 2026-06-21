"""init - 完整初始化 RBAC

Revision ID: d460109141fa
Revises: 
Create Date: 2026-06-19
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd460109141fa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('departments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('sort', sa.Integer(), server_default='0'),
        sa.Column('status', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('roles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.Column('menu_ids', sa.Text(), nullable=True),
        sa.Column('status', sa.Integer(), server_default='1'),
        sa.Column('is_system', sa.Boolean(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_roles_code', 'roles', ['code'], unique=True)
    op.create_table('menus',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('path', sa.String(length=200), nullable=True),
        sa.Column('component', sa.String(length=200), nullable=True),
        sa.Column('permission', sa.String(length=100), nullable=True),
        sa.Column('icon', sa.String(length=64), nullable=True),
        sa.Column('sort', sa.Integer(), server_default='0'),
        sa.Column('visible', sa.Integer(), server_default='1'),
        sa.Column('status', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.Column('dept_id', sa.BigInteger(), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('role_id', sa.BigInteger(), sa.ForeignKey('roles.id'), nullable=True),
        sa.Column('is_super_admin', sa.Boolean(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_table('h5_users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True, comment='姓名'),
        sa.Column('id_card', sa.String(length=18), nullable=True, comment='身份证号'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='手机号'),
        sa.Column('bank_card', sa.String(length=32), nullable=True, comment='银行卡号'),
        sa.Column('bank_card_name', sa.String(length=64), nullable=True, comment='银行卡名称'),
        sa.Column('bank_card_balance', sa.DECIMAL(15, 2), nullable=True, comment='银行卡余额'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_h5_users_username', 'h5_users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_table('h5_users')
    op.drop_table('users')
    op.drop_table('menus')
    op.drop_index('ix_roles_code', table_name='roles')
    op.drop_table('roles')
    op.drop_table('departments')