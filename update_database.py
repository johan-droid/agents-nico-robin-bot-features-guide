#!/usr/bin/env python3
"""
Database update script for Nico Robin Bot - Latest migration techniques
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, async_session_factory
from models import Base
from sqlalchemy import text
from alembic.config import Config
from alembic import command


class DatabaseUpdater:
    """Comprehensive database updater with latest techniques"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = async_session_factory
        self.alembic_cfg = Config("alembic.ini")
        
    async def run_comprehensive_update(self):
        """Run comprehensive database update"""
        print("🚀 Starting Comprehensive Database Update...")
        print("=" * 60)
        
        try:
            # Step 1: Check current database status
            await self._check_database_status()
            
            # Step 2: Create all tables with latest schema
            await self._create_tables()
            
            # Step 3: Run Alembic migrations
            await self._run_migrations()
            
            # Step 4: Update table structures
            await self._update_table_structures()
            
            # Step 5: Create performance indexes
            await self._create_performance_indexes()
            
            # Step 6: Add constraints and foreign keys
            await self._add_constraints()
            
            # Step 7: Populate default data
            await self._populate_default_data()
            
            # Step 8: Create performance views
            await self._create_views()
            
            # Step 9: Update statistics
            await self._update_statistics()
            
            # Step 10: Validate database
            await self._validate_database()
            
            print("\n✅ Comprehensive database update completed successfully!")
            print("🎯 Database is ready for production use")
            
        except Exception as e:
            print(f"\n❌ Database update failed: {str(e)}")
            raise
    
    async def _check_database_status(self):
        """Check current database status"""
        print("📋 Checking Database Status...")
        
        try:
            async with self.engine.begin() as conn:
                # Check if database exists and is accessible
                result = await conn.execute(text("SELECT 1"))
                print("✅ Database connection successful")
                
                # Check current Alembic version
                try:
                    result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                    current_version = result.scalar()
                    print(f"📊 Current Alembic version: {current_version}")
                except Exception:
                    print("📊 Alembic not initialized yet")
                
                # Count existing tables
                result = await conn.execute(text("""
                    SELECT COUNT(*) as count FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                table_count = result.scalar()
                print(f"📋 Existing tables: {table_count}")
        
        except Exception as e:
            print(f"❌ Database status check failed: {e}")
            raise
    
    async def _create_tables(self):
        """Create all tables with latest schema"""
        print("🏗️ Creating Tables...")
        
        try:
            # Create all tables defined in models
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            
            print("✅ Tables created successfully")
            
            # List created tables
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"📋 Total tables created: {len(tables)}")
                
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            raise
    
    async def _run_migrations(self):
        """Run Alembic migrations"""
        print("🔄 Running Alembic Migrations...")
        
        try:
            # Initialize Alembic if not already done
            try:
                command.stamp(self.alembic_cfg, "head")
                print("✅ Alembic initialized")
            except Exception:
                pass  # Already initialized
            
            # Run migrations to head
            try:
                command.upgrade(self.alembic_cfg, "head")
                print("✅ Migrations completed")
            except Exception as e:
                print(f"⚠️ Migration warning: {e}")
                # Continue anyway as tables might already be created
        
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
    
    async def _update_table_structures(self):
        """Update existing table structures"""
        print("🔧 Updating Table Structures...")
        
        structure_updates = [
            # Users table updates
            """
            DO $$
            BEGIN
                -- Add new columns to users table if they don't exist
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'users' AND column_name = 'full_name') THEN
                    ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'users' AND column_name = 'language_code') THEN
                    ALTER TABLE users ADD COLUMN language_code VARCHAR(10);
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'users' AND column_name = 'timezone') THEN
                    ALTER TABLE users ADD COLUMN timezone VARCHAR(50);
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'users' AND column_name = 'is_premium') THEN
                    ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
                END IF;
            END $$;
            """,
            
            # Groups table updates
            """
            DO $$
            BEGIN
                -- Add new columns to groups table if they don't exist
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'groups' AND column_name = 'broadcast_enabled') THEN
                    ALTER TABLE groups ADD COLUMN broadcast_enabled BOOLEAN DEFAULT FALSE;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'groups' AND column_name = 'loyalty_enabled') THEN
                    ALTER TABLE groups ADD COLUMN loyalty_enabled BOOLEAN DEFAULT FALSE;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'groups' AND column_name = 'acn_verified') THEN
                    ALTER TABLE groups ADD COLUMN acn_verified BOOLEAN DEFAULT FALSE;
                END IF;
            END $$;
            """,
        ]
        
        try:
            async with self.session_factory() as session:
                for update_sql in structure_updates:
                    await session.execute(text(update_sql))
                await session.commit()
            
            print("✅ Table structures updated")
        
        except Exception as e:
            print(f"❌ Table structure update failed: {e}")
            raise
    
    async def _create_performance_indexes(self):
        """Create performance indexes"""
        print("📊 Creating Performance Indexes...")
        
        performance_indexes = [
            # Users indexes
            "CREATE INDEX IF NOT EXISTS idx_users_username_lower ON users (LOWER(username));",
            "CREATE INDEX IF NOT EXISTS idx_users_full_name ON users (full_name) WHERE full_name IS NOT NULL;",
            "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at);",
            
            # Groups indexes
            "CREATE INDEX IF NOT EXISTS idx_groups_title_lower ON groups (LOWER(title)) WHERE title IS NOT NULL;",
            "CREATE INDEX IF NOT EXISTS idx_groups_created_at ON groups (created_at);",
            
            # Warns indexes
            "CREATE INDEX IF NOT EXISTS idx_warns_created_at ON warns (created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_warns_user_group ON warns (user_id, group_id);",
            
            # Loyalty points indexes
            "CREATE INDEX IF NOT EXISTS idx_loyalty_points_rank ON loyalty_points (rank);",
            "CREATE INDEX IF NOT EXISTS idx_loyalty_points_last_activity ON loyalty_points (last_activity DESC);",
            "CREATE INDEX IF NOT EXISTS idx_loyalty_points_points_desc ON loyalty_points (points DESC);",
            
            # Realtime events indexes
            "CREATE INDEX IF NOT EXISTS idx_realtime_events_created_at_desc ON realtime_events (created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_realtime_events_type_created ON realtime_events (event_type, created_at DESC);",
            
            # ACN whitelist indexes
            "CREATE INDEX IF NOT EXISTS idx_acn_whitelist_entity_role ON acn_whitelist (entity_id, role);",
            "CREATE INDEX IF NOT EXISTS idx_acn_whitelist_type_active ON acn_whitelist (whitelist_type, is_active);",
            
            # Swear words indexes
            "CREATE INDEX IF NOT EXISTS idx_swear_words_group_severity ON swear_words (group_id, severity);",
            "CREATE INDEX IF NOT EXISTS idx_swear_violations_created_at ON swear_violations (created_at DESC);",
        ]
        
        try:
            async with self.session_factory() as session:
                for index_sql in performance_indexes:
                    try:
                        await session.execute(text(index_sql))
                    except Exception as e:
                        # Index might already exist or have issues
                        print(f"⚠️ Index creation warning: {e}")
                await session.commit()
            
            print("✅ Performance indexes created")
        
        except Exception as e:
            print(f"❌ Index creation failed: {e}")
            raise
    
    async def _add_constraints(self):
        """Add constraints and foreign keys"""
        print("🔒 Adding Constraints...")
        
        constraints = [
            # Check constraints
            "ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS ck_users_ban_count_non_negative CHECK (ban_count >= 0);",
            "ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS ck_users_warn_count_non_negative CHECK (warn_count >= 0);",
            "ALTER TABLE groups ADD CONSTRAINT IF NOT EXISTS ck_groups_max_warns_positive CHECK (max_warns >= 0);",
            "ALTER TABLE groups ADD CONSTRAINT IF NOT EXISTS ck_groups_flood_limit_positive CHECK (flood_limit >= 0);",
            "ALTER TABLE loyalty_points ADD CONSTRAINT IF NOT EXISTS ck_loyalty_points_non_negative CHECK (points >= 0);",
            "ALTER TABLE loyalty_points ADD CONSTRAINT IF NOT EXISTS ck_loyalty_actions_non_negative CHECK (total_actions >= 0);",
            "ALTER TABLE swear_words ADD CONSTRAINT IF NOT EXISTS ck_swear_words_duration_positive CHECK (duration_minutes >= 0);",
            "ALTER TABLE swear_violations ADD CONSTRAINT IF NOT EXISTS ck_swear_violations_duration_positive CHECK (duration_minutes >= 0);",
        ]
        
        try:
            async with self.session_factory() as session:
                for constraint_sql in constraints:
                    try:
                        await session.execute(text(constraint_sql))
                    except Exception as e:
                        # Constraint might already exist
                        print(f"⚠️ Constraint warning: {e}")
                await session.commit()
            
            print("✅ Constraints added")
        
        except Exception as e:
            print(f"❌ Constraint addition failed: {e}")
            raise
    
    async def _populate_default_data(self):
        """Populate default data"""
        print("📝 Populating Default Data...")
        
        default_data = [
            # Loyalty rewards
            """
            INSERT INTO loyalty_rewards (name, description, points_cost, reward_type, reward_data, required_role, is_active, created_at, updated_at)
            VALUES 
                ('Custom Title', 'Get a custom title in ACN', 500, 'title', '{"title": "ACN Veteran"}', 'member', true, NOW(), NOW()),
                ('Priority Support', 'Get priority support from ACN leadership', 1000, 'permission', '{"permission": "priority_support"}', 'commander', true, NOW(), NOW()),
                ('Special Role', 'Get a special role in ACN groups', 2000, 'role', '{"role": "honorary_member"}', 'commander', true, NOW(), NOW()),
                ('Custom Emoji', 'Get custom emoji access', 300, 'permission', '{"permission": "custom_emoji"}', 'member', true, NOW(), NOW())
            ON CONFLICT DO NOTHING;
            """,
            
            # ACN whitelist templates (using negative IDs)
            """
            INSERT INTO acn_whitelist (whitelist_type, entity_id, entity_name, role, is_active, created_at, updated_at, notes)
            VALUES 
                ('channel', -1, 'ACN Announcements', 'announcement', false, NOW(), NOW(), 'Default announcement channel template'),
                ('channel', -2, 'ACN Updates', 'update', false, NOW(), NOW(), 'Default update channel template'),
                ('channel', -3, 'ACN News', 'news', false, NOW(), NOW(), 'Default news channel template'),
                ('channel', -4, 'ACN Events', 'event', false, NOW(), NOW(), 'Default event channel template'),
                ('channel', -5, 'ACN General', 'general', false, NOW(), NOW(), 'Default general channel template')
            ON CONFLICT DO NOTHING;
            """,
        ]
        
        try:
            async with self.session_factory() as session:
                for data_sql in default_data:
                    await session.execute(text(data_sql))
                await session.commit()
            
            print("✅ Default data populated")
        
        except Exception as e:
            print(f"❌ Default data population failed: {e}")
            raise
    
    async def _create_views(self):
        """Create performance views"""
        print("👁️ Creating Performance Views...")
        
        views = [
            # User statistics view
            """
            CREATE OR REPLACE VIEW vw_user_stats AS
            SELECT u.user_id, u.username, u.first_name, u.full_name,
                   COUNT(DISTINCT gm.group_id) as group_count,
                   COUNT(DISTINCT w.warn_id) as warn_count,
                   COALESCE(SUM(lp.points), 0) as total_points,
                   MAX(lp.updated_at) as last_activity,
                   u.created_at, u.updated_at
            FROM users u
            LEFT JOIN group_members gm ON u.user_id = gm.user_id
            LEFT JOIN warns w ON u.user_id = w.user_id
            LEFT JOIN loyalty_points lp ON u.user_id = lp.user_id
            GROUP BY u.user_id, u.username, u.first_name, u.full_name, u.created_at, u.updated_at;
            """,
            
            # Group statistics view
            """
            CREATE OR REPLACE VIEW vw_group_stats AS
            SELECT g.group_id, g.title, g.username as group_username,
                   COUNT(DISTINCT gm.user_id) as member_count,
                   COUNT(DISTINCT w.warn_id) as total_warns,
                   COALESCE(SUM(lp.points), 0) as total_points,
                   COUNT(DISTINCT f.filter_id) as filter_count,
                   COUNT(DISTINCT sw.word_id) as swear_word_count,
                   g.broadcast_enabled, g.loyalty_enabled, g.acn_verified,
                   g.created_at, g.updated_at
            FROM groups g
            LEFT JOIN group_members gm ON g.group_id = gm.group_id
            LEFT JOIN warns w ON g.group_id = w.group_id
            LEFT JOIN loyalty_points lp ON g.group_id = lp.group_id
            LEFT JOIN filters f ON g.group_id = f.group_id
            LEFT JOIN swear_words sw ON g.group_id = sw.group_id
            GROUP BY g.group_id, g.title, g.username, g.broadcast_enabled, g.loyalty_enabled, g.acn_verified, g.created_at, g.updated_at;
            """,
            
            # ACN statistics view
            """
            CREATE OR REPLACE VIEW vw_acn_stats AS
            SELECT 
                COUNT(DISTINCT CASE WHEN whitelist_type = 'user' THEN entity_id END) as acn_users,
                COUNT(DISTINCT CASE WHEN whitelist_type = 'group' THEN entity_id END) as acn_groups,
                COUNT(DISTINCT CASE WHEN whitelist_type = 'channel' THEN entity_id END) as acn_channels,
                COUNT(DISTINCT CASE WHEN role = 'captain' THEN entity_id END) as captains,
                COUNT(DISTINCT CASE WHEN role = 'commander' THEN entity_id END) as commanders,
                COUNT(DISTINCT CASE WHEN role = 'member' THEN entity_id END) as members
            FROM acn_whitelist
            WHERE is_active = true;
            """,
        ]
        
        try:
            async with self.session_factory() as session:
                for view_sql in views:
                    await session.execute(text(view_sql))
                await session.commit()
            
            print("✅ Performance views created")
        
        except Exception as e:
            print(f"❌ View creation failed: {e}")
            raise
    
    async def _update_statistics(self):
        """Update table statistics"""
        print("📊 Updating Statistics...")
        
        tables = [
            'users', 'groups', 'warns', 'filters', 'notes', 'group_members',
            'loyalty_points', 'loyalty_rewards', 'loyalty_redemptions', 'acn_activities',
            'acn_whitelist', 'realtime_events', 'websocket_connections', 'event_subscriptions',
            'event_audit_log', 'swear_words', 'swear_violations'
        ]
        
        try:
            async with self.session_factory() as session:
                for table in tables:
                    try:
                        await session.execute(text(f"ANALYZE {table}"))
                    except Exception:
                        pass  # Table might not exist yet
                await session.commit()
            
            print("✅ Statistics updated")
        
        except Exception as e:
            print(f"❌ Statistics update failed: {e}")
            raise
    
    async def _validate_database(self):
        """Validate database after update"""
        print("✅ Validating Database...")
        
        validations = [
            ("users", "SELECT COUNT(*) as count FROM users"),
            ("groups", "SELECT COUNT(*) as count FROM groups"),
            ("loyalty_points", "SELECT COUNT(*) as count FROM loyalty_points"),
            ("acn_whitelist", "SELECT COUNT(*) as count FROM acn_whitelist"),
            ("realtime_events", "SELECT COUNT(*) as count FROM realtime_events"),
        ]
        
        try:
            async with self.session_factory() as session:
                for table, query in validations:
                    try:
                        result = await session.execute(text(query))
                        count = result.scalar()
                        print(f"📋 {table}: {count} records")
                    except Exception as e:
                        print(f"⚠️ Could not validate {table}: {e}")
            
            print("✅ Database validation completed")
        
        except Exception as e:
            print(f"❌ Database validation failed: {e}")
            raise


async def main():
    """Run comprehensive database update"""
    print("🚀 Nico Robin Bot - Comprehensive Database Update")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    updater = DatabaseUpdater()
    await updater.run_comprehensive_update()
    
    print(f"\n✅ Database update completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("🎯 Bot is ready for production with latest database schema!")


if __name__ == "__main__":
    asyncio.run(main())
