"""initial

Revision ID: 3a2b1c0d
Revises: 
Create Date: 2026-07-03 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a2b1c0d'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'audit_history',
        sa.Column('audit_id', sa.String(), nullable=False),
        sa.Column('repository_id', sa.String(), nullable=False),
        sa.Column('repo_name', sa.String(), nullable=False),
        sa.Column('installation_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('scoring_version', sa.String(), nullable=False),
        sa.Column('devlens_version', sa.String(), nullable=False),
        sa.Column('commit_sha', sa.String(), nullable=False),
        sa.Column('branch', sa.String(), nullable=False),
        sa.Column('audit_duration_ms', sa.Integer(), nullable=False),
        sa.Column('trigger_type', sa.String(), nullable=False),
        sa.Column('warnings_count', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('audit_id')
    )
    op.create_index('idx_installation_timestamp', 'audit_history', ['installation_id', 'timestamp'], unique=False)
    op.create_index('idx_repository_timestamp', 'audit_history', ['repository_id', 'timestamp'], unique=False)

    op.create_table(
        'repository_health',
        sa.Column('repository_id', sa.String(), nullable=False),
        sa.Column('repo_name', sa.String(), nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False),
        sa.Column('last_audit', sa.DateTime(), nullable=False),
        sa.Column('trend', sa.String(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('critical_findings', sa.Integer(), nullable=False),
        sa.Column('documentation_score', sa.Float(), nullable=False),
        sa.Column('security_score', sa.Float(), nullable=False),
        sa.Column('testing_score', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('repository_id')
    )

def downgrade():
    op.drop_table('repository_health')
    op.drop_index('idx_repository_timestamp', table_name='audit_history')
    op.drop_index('idx_installation_timestamp', table_name='audit_history')
    op.drop_table('audit_history')
