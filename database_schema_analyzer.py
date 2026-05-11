#!/usr/bin/env python3
"""
Comprehensive database schema analyzer and migration generator for Nico Robin Bot
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Set

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Base
from models.user import User, GroupMember
from models.group import Group, GroupSettingSnapshot
from models.warn import Warn
from models.note import Note
from models.filter import Filter
from models.federation import Federation, FederationAdmin, FederationBan, FederationGroup
from models.audit import ActionLog, JoinLog, MessageLog
from models.event import RealtimeEvent, WebSocketConnection, EventSubscription, EventAuditLog
from models.swear_word import SwearWord, SwearViolation
from models.loyalty import ACNWhitelist, LoyaltyPoints, LoyaltyReward, LoyaltyRedemption, ACNActivity

from sqlalchemy import inspect
from sqlalchemy.schema import CreateTable, CreateIndex


class DatabaseSchemaAnalyzer:
    """Analyzes the current database schema and generates comprehensive migrations"""
    
    def __init__(self):
        self.metadata = Base.metadata
        self.tables = self.metadata.tables
        self.relationships = {}
        self.constraints = {}
        
    def analyze_schema(self) -> Dict:
        """Analyze the complete database schema"""
        analysis = {
            "tables": {},
            "relationships": {},
            "constraints": {},
            "indexes": {},
            "foreign_keys": {},
            "total_tables": len(self.tables),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Analyze each table
        for table_name, table in self.tables.items():
            table_analysis = self._analyze_table(table)
            analysis["tables"][table_name] = table_analysis
            
            # Collect relationships
            for fk in table.foreign_keys:
                if table_name not in analysis["foreign_keys"]:
                    analysis["foreign_keys"][table_name] = []
                analysis["foreign_keys"][table_name].append({
                    "column": fk.column.name,
                    "target_table": fk.column.table.name,
                    "target_column": fk.column.references,
                    "ondelete": fk.ondelete,
                    "onupdate": fk.onupdate
                })
        
        return analysis
    
    def _analyze_table(self, table) -> Dict:
        """Analyze individual table structure"""
        columns = {}
        indexes = []
        constraints = []
        
        for column in table.columns:
            columns[column.name] = {
                "type": str(column.type),
                "nullable": column.nullable,
                "primary_key": column.primary_key,
                "unique": column.unique,
                "default": str(column.default) if column.default else None,
                "foreign_key": str(column.foreign_keys) if column.foreign_keys else None
            }
        
        for index in table.indexes:
            indexes.append({
                "name": index.name,
                "columns": [col.name for col in index.columns],
                "unique": index.unique
            })
        
        for constraint in table.constraints:
            constraints.append({
                "name": constraint.name,
                "type": type(constraint).__name__,
                "columns": getattr(constraint, "columns", [])
            })
        
        return {
            "name": table.name,
            "columns": columns,
            "indexes": indexes,
            "constraints": constraints,
            "column_count": len(columns),
            "index_count": len(indexes),
            "constraint_count": len(constraints)
        }
    
    def generate_comprehensive_migration(self) -> str:
        """Generate a comprehensive migration for the latest schema"""
        migration = f'''"""
Comprehensive database schema update for Nico Robin Bot

Revision ID: 2024_01_05_comprehensive_schema_update
Revises: 2024_01_04_add_broadcast_channels
Create Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2024_01_05_comprehensive_schema_update'
down_revision: Union[str, None] = '2024_01_04_add_broadcast_channels'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database to latest schema with comprehensive optimizations"""
    
    # Create all tables with proper constraints and indexes
    _create_tables()
    
    # Create optimized indexes for performance
    _create_performance_indexes()
    
    # Add proper constraints and foreign keys
    _add_constraints()
    
    # Update existing tables with new columns if needed
    _update_existing_tables()
    
    # Populate default data
    _populate_default_data()


def _create_tables() -> None:
    """Create all database tables"""
'''
        
        # Generate table creation code for each table
        for table_name in sorted(self.tables.keys()):
            if table_name not in ['users', 'groups']:  # Skip core tables that likely exist
                table = self.tables[table_name]
                migration += f'\n    # Create {table_name} table\n'
                migration += f'    op.create_table(\n'
                migration += f'        \'{table_name}\',\n'
                
                columns = []
                for column in table.columns:
                    column_def = f'        sa.Column(\'{column.name}\', {self._get_column_type(column)}'
                    if not column.nullable:
                        column_def += ', nullable=False'
                    if column.primary_key:
                        column_def += ', primary_key=True'
                    if column.default:
                        column_def += f', server_default={self._get_default_value(column)}'
                    column_def += ')'
                    columns.append(column_def)
                
                migration += ',\n'.join(columns)
                
                # Add constraints
                if table.constraints:
                    migration += ',\n'
                    for constraint in table.constraints:
                        migration += f'        {self._get_constraint_definition(constraint)},\n'
                
                migration += f'    )\n'
        
        migration += '''
    
    # Create indexes for all tables
    _create_table_indexes()


def _create_table_indexes() -> None:
    """Create indexes for optimal performance"""
'''
        
        # Generate index creation code
        for table_name in sorted(self.tables.keys()):
            table = self.tables[table_name]
            for index in table.indexes:
                if not index.unique:  # Skip unique constraints (handled separately)
                    migration += f'\n    # Create index for {table_name}.{index.name}\n'
                    migration += f'    op.create_index(\n'
                    migration += f'        \'{index.name}\', \'{table_name}\', \n'
                    migration += f'        [{", ".join([f"\'{col.name}\'" for col in index.columns])}]\n'
                    migration += f'    )\n'
        
        migration += '''
    
    # Add foreign key constraints
    _add_foreign_keys()


def _add_foreign_keys() -> None:
    """Add foreign key constraints with proper cascading"""
'''
        
        # Generate foreign key constraints
        for table_name in sorted(self.tables.keys()):
            table = self.tables[table_name]
            for fk in table.foreign_keys:
                migration += f'\n    # Add foreign key for {table_name}.{fk.column.name}\n'
                migration += f'    op.create_foreign_key(\n'
                migration += f'        \'fk_{table_name}_{fk.column.name}_{fk.column.table.name}\',\n'
                migration += f'        \'{table_name}\', \'{fk.column.name}\', \n'
                migration += f'        \'{fk.column.table.name}\', \'{fk.column.references}\''
                if fk.ondelete:
                    migration += f',\n        ondelete=\'{fk.ondelete}\''
                if fk.onupdate:
                    migration += f',\n        onupdate=\'{fk.onupdate}\''
                migration += f'\n    )\n'
        
        migration += '''
    
    # Add unique constraints
    _add_unique_constraints()


def _add_unique_constraints() -> None:
    """Add unique constraints for data integrity"""
'''
        
        # Generate unique constraints
        for table_name in sorted(self.tables.keys()):
            table = self.tables[table_name]
            for constraint in table.constraints:
                if 'unique' in str(constraint).lower():
                    migration += f'\n    # Add unique constraint for {table_name}\n'
                    migration += f'    op.create_unique_constraint(\n'
                    migration += f'        \'{constraint.name}\', \'{table_name}\', \n'
                    if hasattr(constraint, 'columns'):
                        migration += f'        [{", ".join([f"\'{col}\'" for col in constraint.columns])}]\n'
                    else:
                        migration += f'        [\'column_name\']\n'
                    migration += f'    )\n'
        
        migration += '''
    
    # Add check constraints for data validation
    _add_check_constraints()


def _add_check_constraints() -> None:
    """Add check constraints for data validation"""
'''
        
        # Add check constraints for critical validations
        check_constraints = [
            ('groups', 'ck_groups_max_warns_positive', 'max_warns >= 0'),
            ('groups', 'ck_groups_flood_limit_positive', 'flood_limit >= 0'),
            ('users', 'ck_users_ban_count_non_negative', 'ban_count >= 0'),
            ('users', 'ck_users_warn_count_non_negative', 'warn_count >= 0'),
            ('loyalty_points', 'ck_loyalty_points_non_negative', 'points >= 0'),
            ('loyalty_points', 'ck_loyalty_actions_non_negative', 'total_actions >= 0'),
        ]
        
        for table, name, condition in check_constraints:
            migration += f'\n    # Add check constraint for {table}\n'
            migration += f'    op.create_check_constraint(\n'
            migration += f'        \'{name}\', \'{table}\', \n'
            migration += f'        sa.text(\'{condition}\')\n'
            migration += f'    )\n'
        
        migration += '''
    
    # Update existing tables with new columns if needed
    _update_existing_tables()


def _update_existing_tables() -> None:
    """Update existing tables with new columns and constraints"""
'''
        
        # Add any missing columns to existing tables
        updates = [
            ('users', 'full_name', sa.String(length=255), "User's full name"),
            ('users', 'language_code', sa.String(length=10), "User's preferred language"),
            ('users', 'timezone', sa.String(length=50), "User's timezone"),
            ('users', 'is_premium', sa.Boolean(), "Premium user status"),
        ]
        
        for table, column, column_type, description in updates:
            migration += f'\n    # Add {column} to {table} - {description}\n'
            migration += f'    if not _column_exists(\'{table}\', \'{column}\'):\n'
            migration += f'        op.add_column(\'{table}\', sa.Column(\'{column}\', {column_type}, nullable=True))\n'
        
        migration += '''
    
    # Populate default data
    _populate_default_data()


def _populate_default_data() -> None:
    """Populate default data for new features"""
'''
        
        # Add default data for new features
        default_data = [
            ('loyalty_rewards', [
                {
                    'name': 'Custom Title',
                    'description': 'Get a custom title in ACN',
                    'points_cost': 500,
                    'reward_type': 'title',
                    'reward_data': '{"title": "ACN Veteran"}',
                    'required_role': 'member'
                },
                {
                    'name': 'Priority Support',
                    'description': 'Get priority support from ACN leadership',
                    'points_cost': 1000,
                    'reward_type': 'permission',
                    'reward_data': '{"permission": "priority_support"}',
                    'required_role': 'commander'
                }
            ])
        ]
        
        for table, data in default_data:
            migration += f'\n    # Populate default {table} data\n'
            for item in data:
                migration += f'    op.execute("""\n'
                migration += f'        INSERT INTO {table} (name, description, points_cost, reward_type, reward_data, required_role, is_active, created_at, updated_at)\n'
                migration += f'        VALUES (\n'
                migration += f'            \'{item["name"]}\', \'{item["description"]}\', {item["points_cost"]}, \'{item["reward_type"]}\', \'{item["reward_data"]}\', \'{item["required_role"]}\', true, NOW(), NOW()\n'
                migration += f'        )\n'
                migration += f'        ON CONFLICT DO NOTHING\n'
                migration += f'    """)\n'
        
        migration += '''
    
    # Create performance views
    _create_performance_views()


def _create_performance_views() -> None:
    """Create optimized views for common queries"""
'''
        
        # Create performance views
        views = [
            ('vw_user_stats', '''
                SELECT u.user_id, u.username, u.first_name, 
                       COUNT(DISTINCT gm.group_id) as group_count,
                       COUNT(DISTINCT w.warn_id) as warn_count,
                       COUNT(DISTINCT lp.points_id) as total_points,
                       MAX(lp.updated_at) as last_activity
                FROM users u
                LEFT JOIN group_members gm ON u.user_id = gm.user_id
                LEFT JOIN warns w ON u.user_id = w.user_id
                LEFT JOIN loyalty_points lp ON u.user_id = lp.user_id
                GROUP BY u.user_id, u.username, u.first_name
            '''),
            ('vw_group_stats', '''
                SELECT g.group_id, g.title, g.username as group_username,
                       COUNT(DISTINCT gm.user_id) as member_count,
                       COUNT(DISTINCT w.warn_id) as total_warns,
                       COUNT(DISTINCT lp.points_id) as total_points,
                       COUNT(DISTINCT f.filter_id) as filter_count
                FROM groups g
                LEFT JOIN group_members gm ON g.group_id = gm.group_id
                LEFT JOIN warns w ON g.group_id = w.group_id
                LEFT JOIN loyalty_points lp ON g.group_id = lp.group_id
                LEFT JOIN filters f ON g.group_id = f.group_id
                GROUP BY g.group_id, g.title, g.username
            ''')
        ]
        
        for view_name, view_sql in views:
            migration += f'\n    # Create view {view_name}\n'
            migration += f'    op.execute("""\n'
            migration += f'        CREATE OR REPLACE VIEW {view_name} AS\n'
            migration += f'        {view_sql}\n'
            migration += f'    """)\n'
        
        migration += '''
    
    # Update table statistics for query optimization
    _update_table_statistics()


def _update_table_statistics() -> None:
    """Update table statistics for query optimization"""
'''
        
        # Update statistics for all tables
        tables = ['users', 'groups', 'warns', 'filters', 'loyalty_points', 'realtime_events']
        
        for table in tables:
            migration += f'\n    # Update statistics for {table}\n'
            migration += f'    op.execute(f"ANALYZE {table}")\n'
        
        migration += '''
    
    # Create optimized indexes for performance
    _create_performance_indexes()


def _create_performance_indexes() -> None:
    """Create additional performance indexes"""
'''
        
        # Add performance indexes
        performance_indexes = [
            ('users', 'idx_users_username_lower', 'lower(username)'),
            ('users', 'idx_users_full_name', 'full_name'),
            ('groups', 'idx_groups_title_lower', 'lower(title)'),
            ('warns', 'idx_warnings_created_at', 'created_at'),
            ('loyalty_points', 'idx_loyalty_points_rank', 'rank'),
            ('loyalty_points', 'idx_loyalty_points_last_activity', 'last_activity'),
            ('realtime_events', 'idx_realtime_events_created_at_desc', 'created_at DESC'),
            ('acn_whitelist', 'idx_acn_whitelist_entity_role', 'entity_id, role'),
        ]
        
        for table, index_name, columns in performance_indexes:
            migration += f'\n    # Create performance index {index_name}\n'
            migration += f'    op.create_index(\'{index_name}\', \'{table}\', \'{columns}\')\n'
        
        migration += '''
    
    # Add table comments for documentation
    _add_table_comments()


def _add_table_comments() -> None:
    """Add table and column comments for documentation"""
'''
        
        # Add table comments
        table_comments = [
            ('users', 'User accounts and their metadata'),
            ('groups', 'Telegram groups and their settings'),
            ('warns', 'Warning records for users'),
            ('filters', 'Message filters for groups'),
            ('loyalty_points', 'ACN loyalty points and ranks'),
            ('realtime_events', 'Real-time event tracking'),
            ('acn_whitelist', 'Anime Crew Network whitelist'),
        ]
        
        for table, comment in table_comments:
            migration += f'\n    # Add comment to {table}\n'
            migration += f'    op.execute(f"COMMENT ON TABLE {table} IS \'{comment}\'")\n'
        
        migration += '''
    
    # Validate database integrity
    _validate_database_integrity()


def _validate_database_integrity() -> None:
    """Validate database integrity and consistency"""
'''
        
        # Add integrity checks
        integrity_checks = [
            'SELECT COUNT(*) FROM users WHERE user_id < 0',  # No negative user IDs
            'SELECT COUNT(*) FROM groups WHERE group_id < 0',  # No negative group IDs
            'SELECT COUNT(*) FROM warns WHERE user_id NOT IN (SELECT user_id FROM users)',  # Orphaned warns
            'SELECT COUNT(*) FROM loyalty_points WHERE user_id NOT IN (SELECT user_id FROM users)',  # Orphaned loyalty points
        ]
        
        for check in integrity_checks:
            migration += f'\n    # Integrity check: {check}\n'
            migration += f'    result = op.execute(f"{check}").scalar()\n'
            migration += f'    if result > 0:\n'
            migration += f'        print(f"Warning: Found {{result}} integrity issues")\n'
        
        migration += '''
    
    print("✅ Comprehensive database schema update completed successfully")


def downgrade() -> None:
    """Downgrade database to previous schema"""
    
    # Drop views
    _drop_performance_views()
    
    # Drop performance indexes
    _drop_performance_indexes()
    
    # Drop new tables
    _drop_new_tables()
    
    # Remove new columns
    _remove_new_columns()
    
    print("✅ Database downgrade completed")


def _drop_performance_views() -> None:
    """Drop performance views"""
'''
        
        # Drop views in reverse order
        views = ['vw_user_stats', 'vw_group_stats']
        
        for view_name in reversed(views):
            migration += f'\n    # Drop view {view_name}\n'
            migration += f'    op.execute(f"DROP VIEW IF EXISTS {view_name}")\n'
        
        migration += '''
    
    def _drop_performance_indexes() -> None:
        """Drop performance indexes"""
'''
        
        # Drop performance indexes
        performance_indexes = [
            ('idx_users_username_lower', 'users'),
            ('idx_users_full_name', 'users'),
            ('idx_groups_title_lower', 'groups'),
            ('idx_warnings_created_at', 'warns'),
            ('idx_loyalty_points_rank', 'loyalty_points'),
            ('idx_loyalty_points_last_activity', 'loyalty_points'),
            ('idx_realtime_events_created_at_desc', 'realtime_events'),
            ('idx_acn_whitelist_entity_role', 'acn_whitelist'),
        ]
        
        for index_name, table in reversed(performance_indexes):
            migration += f'\n    # Drop index {index_name}\n'
            migration += f'    op.drop_index(\'{index_name}\', table_name=\'{table}\')\n'
        
        migration += '''
    
    def _drop_new_tables() -> None:
        """Drop newly created tables"""
'''
        
        # Drop tables in reverse order of creation
        new_tables = [
            'acn_activities',
            'loyalty_redemptions', 
            'loyalty_rewards',
            'loyalty_points',
            'acn_whitelist',
            'event_audit_log',
            'event_subscriptions',
            'websocket_connections',
            'realtime_events',
            'swear_violations',
            'swear_words',
            'message_logs',
            'join_logs',
            'action_logs',
            'notes',
            'filters',
            'federation_bans',
            'federation_admins',
            'federation_groups',
            'federation',
            'group_setting_snapshots',
            'group_members',
            'warns'
        ]
        
        for table in reversed(new_tables):
            migration += f'\n    # Drop table {table}\n'
            migration += f'    op.drop_table(\'{table}\')\n'
        
        migration += '''
    
    def _remove_new_columns() -> None:
        """Remove newly added columns"""
'''
        
        # Remove new columns
        new_columns = [
            ('users', 'full_name'),
            ('users', 'language_code'),
            ('users', 'timezone'),
            ('users', 'is_premium'),
        ]
        
        for table, column in reversed(new_columns):
            migration += f'\n    # Remove column {column} from {table}\n'
            migration += f'    if _column_exists(\'{table}\', \'{column}\'):\n'
            migration += f'        op.drop_column(\'{table}\', \'{column}\')\n'
        
        migration += '''
    
    def _column_exists(table_name: str, column_name: str) -> bool:
        """Check if column exists in table"""
        conn = op.get_bind()
        inspector = inspect(conn)
        columns = [col["name"] for col in inspector.get_columns(table_name)]
        return column_name in columns


# Helper functions
def _column_exists(table_name: str, column_name: str) -> bool:
    """Check if column exists in table"""
    conn = op.get_bind()
    inspector = inspect(conn)
    try:
        columns = [col["name"] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False
'''
        
        return migration
    
    def _get_column_type(self, column):
        """Get SQLAlchemy column type definition"""
        type_str = str(column.type)
        if 'INTEGER' in type_str:
            return 'sa.Integer()'
        elif 'BIGINT' in type_str:
            return 'sa.BigInteger()'
        elif 'VARCHAR' in type_str:
            return f'sa.String(length={column.type.length})'
        elif 'TEXT' in type_str:
            return 'sa.Text()'
        elif 'BOOLEAN' in type_str:
            return 'sa.Boolean()'
        elif 'DATETIME' in type_str:
            return 'sa.DateTime(timezone=True)'
        elif 'JSON' in type_str:
            return 'sa.JSON()'
        else:
            return f'sa.String()'
    
    def _get_default_value(self, column):
        """Get default value definition"""
        if column.default is None:
            return 'None'
        default_str = str(column.default)
        if 'now()' in default_str:
            return 'sa.func.now()'
        elif 'true' in default_str:
            return 'sa.text(\'true\')'
        elif 'false' in default_str:
            return 'sa.text(\'false\')'
        elif default_str.isdigit():
            return f'sa.text(\'{default_str}\')'
        else:
            return f'sa.text(\'{default_str}\')'
    
    def _get_constraint_definition(self, constraint):
        """Get constraint definition"""
        if hasattr(constraint, 'columns'):
            columns = getattr(constraint, 'columns', [])
            if columns:
                return f'sa.UniqueConstraint({", ".join([f"\'{col}\'" for col in columns])})'
        return f'sa.Constraint(\'{constraint.name}\')'


async def main():
    """Run the database schema analysis"""
    print("🔍 Analyzing Nico Robin Bot Database Schema...")
    print("=" * 60)
    
    analyzer = DatabaseSchemaAnalyzer()
    analysis = analyzer.analyze_schema()
    
    print(f"📊 Total Tables: {analysis['total_tables']}")
    print(f"🔗 Foreign Keys: {len(analysis['foreign_keys'])}")
    print(f"⏰ Analysis Time: {analysis['analysis_timestamp']}")
    
    print("\n📋 Tables Found:")
    for table_name, table_info in analysis['tables'].items():
        print(f"• {table_name}: {table_info['column_count']} columns, {table_info['index_count']} indexes")
    
    print(f"\n🔗 Foreign Key Relationships:")
    for table, fks in analysis['foreign_keys'].items():
        if fks:
            print(f"• {table}: {len(fks)} foreign keys")
    
    # Generate comprehensive migration
    print("\n🚀 Generating Comprehensive Migration...")
    migration = analyzer.generate_comprehensive_migration()
    
    # Save migration to file
    with open('comprehensive_schema_update.py', 'w') as f:
        f.write(migration)
    
    print("✅ Migration saved to 'comprehensive_schema_update.py'")
    print("🎯 Ready to apply with 'alembic upgrade head'")
    
    # Generate summary
    summary = {
        "total_tables": analysis['total_tables'],
        "total_columns": sum(info['column_count'] for info in analysis['tables'].values()),
        "total_indexes": sum(info['index_count'] for info in analysis['tables'].values()),
        "total_constraints": sum(info['constraint_count'] for info in analysis['tables'].values()),
        "foreign_keys": len(analysis['foreign_keys']),
        "migration_generated": True
    }
    
    print(f"\n📈 Summary:")
    for key, value in summary.items():
        print(f"• {key.replace('_', ' ').title()}: {value}")
    
    return analysis, migration


if __name__ == "__main__":
    asyncio.run(main())
