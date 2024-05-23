"""Add story persons

Revision ID: 81d9a9ce57dc
Revises: 887b3cbc657d
Create Date: 2024-05-15 10:01:35.634886+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81d9a9ce57dc'
down_revision: Union[str, None] = '887b3cbc657d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('persons',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('story_persons',
    sa.Column('story_id', sa.Integer(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('story_persons')
    op.drop_table('persons')
    # ### end Alembic commands ###
