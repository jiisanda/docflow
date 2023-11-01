"""Initial Almebic

Revision ID: 2a02384ab925
Revises: 
Create Date: 2023-11-01 20:51:23.621851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2a02384ab925'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notify',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('receiver_id', sa.String(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('read', 'unread', name='notifyenum'), nullable=True),
    sa.Column('notified_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notify_id'), 'notify', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('user_since', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    op.create_table('document_metadata',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('s3_url', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('file_type', sa.String(), nullable=True),
    sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('categories', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('status', sa.Enum('public', 'private', 'shared', 'deleted', 'archived', name='statusenum'), nullable=True),
    sa.Column('file_hash', sa.String(), nullable=True),
    sa.Column('access_to', sa.ARRAY(sa.String()), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('s3_url')
    )
    op.create_index(op.f('ix_document_metadata_id'), 'document_metadata', ['id'], unique=False)
    op.create_table('share_url',
    sa.Column('url_id', sa.String(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('visits', sa.Integer(), nullable=True),
    sa.Column('share_to', sa.ARRAY(sa.String()), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('url_id'),
    sa.UniqueConstraint('filename'),
    sa.UniqueConstraint('url'),
    sa.UniqueConstraint('url_id')
    )
    op.create_table('doc_user_access',
    sa.Column('doc_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', sa.String(length=26), nullable=True),
    sa.ForeignKeyConstraint(['doc_id'], ['document_metadata.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.UniqueConstraint('doc_id', 'user_id', name='uq_doc_user_access_doc_user')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('doc_user_access')
    op.drop_table('share_url')
    op.drop_index(op.f('ix_document_metadata_id'), table_name='document_metadata')
    op.drop_table('document_metadata')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_notify_id'), table_name='notify')
    op.drop_table('notify')
    # ### end Alembic commands ###
