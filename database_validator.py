#!/usr/bin/env python3
"""
Comprehensive database validation and testing script for Nico Robin Bot
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Set, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, async_session_factory
from models import Base
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseValidator:
    """Comprehensive database validation and testing"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = async_session_factory
        self.validation_results = {}
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive database validation"""
        print("🔍 Starting Comprehensive Database Validation...")
        print("=" * 60)
        
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "validations": {},
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
        # Run all validations
        await self._validate_schema_integrity(validation_results)
        await self._validate_foreign_keys(validation_results)
        await self._validate_data_consistency(validation_results)
        await self._validate_indexes(validation_results)
        await self._validate_constraints(validation_results)
        await self._test_database_operations(validation_results)
        await self._validate_performance_views(validation_results)
        
        # Generate summary
        self._generate_summary(validation_results)
        
        return validation_results
    
    async def _validate_schema_integrity(self, results: Dict[str, Any]):
        """Validate database schema integrity"""
        print("📋 Validating Schema Integrity...")
        
        schema_validation = {
            "expected_tables": [],
            "missing_tables": [],
            "extra_tables": [],
            "table_validations": {}
        }
        
        try:
            # Get expected tables from models
            expected_tables = set(Base.metadata.tables.keys())
            schema_validation["expected_tables"] = list(expected_tables)
            
            # Get actual tables from database
            async with self.engine.begin() as conn:
                inspector = inspect(conn)
                actual_tables = set(inspector.get_table_names())
            
            # Compare tables
            missing_tables = expected_tables - actual_tables
            extra_tables = actual_tables - expected_tables
            
            schema_validation["missing_tables"] = list(missing_tables)
            schema_validation["extra_tables"] = list(extra_tables)
            
            # Validate each table structure
            for table_name in expected_tables:
                if table_name in actual_tables:
                    table_validation = await self._validate_table_structure(table_name)
                    schema_validation["table_validations"][table_name] = table_validation
            
            # Record results
            results["validations"]["schema_integrity"] = schema_validation
            
            # Log results
            if missing_tables:
                results["errors"].append(f"Missing tables: {missing_tables}")
            
            if extra_tables:
                results["warnings"].append(f"Extra tables found: {extra_tables}")
            
            print(f"✅ Schema validation: {len(expected_tables)} expected, {len(actual_tables)} found")
            
        except Exception as e:
            results["errors"].append(f"Schema validation failed: {str(e)}")
            print(f"❌ Schema validation error: {e}")
    
    async def _validate_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Validate individual table structure"""
        table_validation = {
            "columns": {},
            "indexes": {},
            "foreign_keys": {},
            "constraints": {},
            "issues": []
        }
        
        try:
            async with self.engine.begin() as conn:
                inspector = inspect(conn)
                
                # Get model table
                model_table = Base.metadata.tables[table_name]
                
                # Validate columns
                actual_columns = {col["name"]: col for col in inspector.get_columns(table_name)}
                expected_columns = {col.name: col for col in model_table.columns}
                
                for col_name, expected_col in expected_columns.items():
                    if col_name in actual_columns:
                        actual_col = actual_columns[col_name]
                        column_issues = []
                        
                        # Check column type
                        if str(expected_col.type) != str(actual_col["type"]):
                            column_issues.append(f"Type mismatch: expected {expected_col.type}, got {actual_col['type']}")
                        
                        # Check nullable
                        if expected_col.nullable != actual_col["nullable"]:
                            column_issues.append(f"Nullable mismatch: expected {expected_col.nullable}, got {actual_col['nullable']}")
                        
                        # Check primary key
                        if expected_col.primary_key != actual_col.get("primary_key", False):
                            column_issues.append(f"Primary key mismatch")
                        
                        if column_issues:
                            table_validation["columns"][col_name] = {"issues": column_issues}
                            table_validation["issues"].extend([f"{col_name}: {issue}" for issue in column_issues])
                    else:
                        table_validation["issues"].append(f"Missing column: {col_name}")
                
                # Validate indexes
                expected_indexes = {idx.name: idx for idx in model_table.indexes}
                actual_indexes = {idx["name"]: idx for idx in inspector.get_indexes(table_name)}
                
                for idx_name, expected_idx in expected_indexes.items():
                    if idx_name not in actual_indexes:
                        table_validation["issues"].append(f"Missing index: {idx_name}")
                    else:
                        # Check index columns
                        expected_cols = [col.name for col in expected_idx.columns]
                        actual_cols = actual_indexes[idx_name]["column_names"]
                        
                        if set(expected_cols) != set(actual_cols):
                            table_validation["indexes"][idx_name] = {
                                "issues": [f"Column mismatch: expected {expected_cols}, got {actual_cols}"]
                            }
                            table_validation["issues"].append(f"Index {idx_name}: column mismatch")
                
                # Validate foreign keys
                expected_fks = {fk.column.name: fk for fk in model_table.foreign_keys}
                actual_fks = {fk["constrained_columns"][0]: fk for fk in inspector.get_foreign_keys(table_name)}
                
                for fk_name, expected_fk in expected_fks.items():
                    if fk_name not in actual_fks:
                        table_validation["issues"].append(f"Missing foreign key: {fk_name}")
                    else:
                        actual_fk = actual_fks[fk_name]
                        expected_target = f"{expected_fk.column.table.name}.{expected_fk.column.references}"
                        actual_target = f"{actual_fk['referred_table']}.{actual_fk['referred_columns'][0]}"
                        
                        if expected_target != actual_target:
                            table_validation["foreign_keys"][fk_name] = {
                                "issues": [f"Target mismatch: expected {expected_target}, got {actual_target}"]
                            }
                            table_validation["issues"].append(f"Foreign key {fk_name}: target mismatch")
        
        except Exception as e:
            table_validation["issues"].append(f"Validation error: {str(e)}")
        
        return table_validation
    
    async def _validate_foreign_keys(self, results: Dict[str, Any]):
        """Validate foreign key relationships"""
        print("🔗 Validating Foreign Keys...")
        
        fk_validation = {
            "orphaned_records": {},
            "missing_references": {},
            "issues": []
        }
        
        try:
            async with self.session_factory() as session:
                # Check for orphaned records in key tables
                orphan_checks = [
                    ("warns", "user_id", "users", "user_id"),
                    ("warns", "group_id", "groups", "group_id"),
                    ("loyalty_points", "user_id", "users", "user_id"),
                    ("loyalty_points", "group_id", "groups", "group_id"),
                    ("acn_activities", "user_id", "users", "user_id"),
                    ("acn_activities", "group_id", "groups", "group_id"),
                    ("realtime_events", "user_id", "users", "user_id"),
                    ("realtime_events", "group_id", "groups", "group_id"),
                    ("swear_violations", "user_id", "users", "user_id"),
                    ("swear_violations", "group_id", "groups", "group_id"),
                ]
                
                for table, fk_column, ref_table, ref_column in orphan_checks:
                    try:
                        query = text(f"""
                            SELECT COUNT(*) as count 
                            FROM {table} t 
                            LEFT JOIN {ref_table} r ON t.{fk_column} = r.{ref_column}
                            WHERE r.{ref_column} IS NULL
                        """)
                        result = await session.execute(query)
                        orphan_count = result.scalar()
                        
                        if orphan_count > 0:
                            fk_validation["orphaned_records"][f"{table}.{fk_column}"] = orphan_count
                            fk_validation["issues"].append(f"Orphaned records in {table}.{fk_column}: {orphan_count}")
                    except Exception as e:
                        fk_validation["issues"].append(f"Error checking {table}.{fk_column}: {str(e)}")
            
            results["validations"]["foreign_keys"] = fk_validation
            
            if fk_validation["issues"]:
                print(f"⚠️  Foreign key issues found: {len(fk_validation['issues'])}")
            else:
                print("✅ Foreign key validation passed")
        
        except Exception as e:
            results["errors"].append(f"Foreign key validation failed: {str(e)}")
            print(f"❌ Foreign key validation error: {e}")
    
    async def _validate_data_consistency(self, results: Dict[str, Any]):
        """Validate data consistency"""
        print("🔍 Validating Data Consistency...")
        
        consistency_validation = {
            "invalid_data": {},
            "data_anomalies": {},
            "issues": []
        }
        
        try:
            async with self.session_factory() as session:
                # Check for invalid data
                consistency_checks = [
                    ("users", "user_id < 0", "Negative user IDs"),
                    ("users", "ban_count < 0", "Negative ban counts"),
                    ("users", "warn_count < 0", "Negative warn counts"),
                    ("groups", "group_id < 0", "Negative group IDs"),
                    ("groups", "max_warns < 0", "Negative max warns"),
                    ("groups", "flood_limit < 0", "Negative flood limits"),
                    ("loyalty_points", "points < 0", "Negative loyalty points"),
                    ("loyalty_points", "total_actions < 0", "Negative total actions"),
                    ("swear_words", "duration_minutes < 0", "Negative duration minutes"),
                    ("swear_violations", "duration_minutes < 0", "Negative violation duration"),
                ]
                
                for table, condition, description in consistency_checks:
                    try:
                        query = text(f"SELECT COUNT(*) as count FROM {table} WHERE {condition}")
                        result = await session.execute(query)
                        invalid_count = result.scalar()
                        
                        if invalid_count > 0:
                            consistency_validation["invalid_data"][table] = {
                                "condition": condition,
                                "count": invalid_count,
                                "description": description
                            }
                            consistency_validation["issues"].append(f"{description}: {invalid_count} records")
                    except Exception as e:
                        consistency_validation["issues"].append(f"Error checking {table}: {str(e)}")
                
                # Check for data anomalies
                anomaly_checks = [
                    ("users", "username IS NULL AND first_name IS NULL", "Users without name"),
                    ("groups", "title IS NULL AND username IS NULL", "Groups without name"),
                    ("warns", "reason IS NULL OR reason = ''", "Warnings without reason"),
                    ("loyalty_points", "points > 0 AND rank = 'Crew Member'", "High points with default rank"),
                ]
                
                for table, condition, description in anomaly_checks:
                    try:
                        query = text(f"SELECT COUNT(*) as count FROM {table} WHERE {condition}")
                        result = await session.execute(query)
                        anomaly_count = result.scalar()
                        
                        if anomaly_count > 0:
                            consistency_validation["data_anomalies"][table] = {
                                "condition": condition,
                                "count": anomaly_count,
                                "description": description
                            }
                            consistency_validation["issues"].append(f"{description}: {anomaly_count} records")
                    except Exception as e:
                        consistency_validation["issues"].append(f"Error checking {table}: {str(e)}")
            
            results["validations"]["data_consistency"] = consistency_validation
            
            if consistency_validation["issues"]:
                print(f"⚠️  Data consistency issues: {len(consistency_validation['issues'])}")
            else:
                print("✅ Data consistency validation passed")
        
        except Exception as e:
            results["errors"].append(f"Data consistency validation failed: {str(e)}")
            print(f"❌ Data consistency validation error: {e}")
    
    async def _validate_indexes(self, results: Dict[str, Any]):
        """Validate database indexes"""
        print("📊 Validating Indexes...")
        
        index_validation = {
            "missing_indexes": [],
            "unused_indexes": [],
            "duplicate_indexes": [],
            "issues": []
        }
        
        try:
            async with self.engine.begin() as conn:
                inspector = inspect(conn)
                
                # Check for expected indexes
                for table_name, table in Base.metadata.tables.items():
                    try:
                        actual_indexes = {idx["name"]: idx for idx in inspector.get_indexes(table_name)}
                        expected_indexes = {idx.name: idx for idx in table.indexes}
                        
                        # Check for missing indexes
                        for expected_idx_name in expected_indexes:
                            if expected_idx_name not in actual_indexes:
                                index_validation["missing_indexes"].append(f"{table_name}.{expected_idx_name}")
                                index_validation["issues"].append(f"Missing index: {table_name}.{expected_idx_name}")
                        
                        # Check for duplicate indexes
                        index_signatures = {}
                        for idx_name, idx_info in actual_indexes.items():
                            signature = tuple(sorted(idx_info["column_names"]))
                            if signature in index_signatures:
                                index_validation["duplicate_indexes"].append({
                                    "table": table_name,
                                    "indexes": [index_signatures[signature], idx_name]
                                })
                                index_validation["issues"].append(f"Duplicate indexes in {table_name}")
                            else:
                                index_signatures[signature] = idx_name
                    
                    except Exception as e:
                        index_validation["issues"].append(f"Error checking indexes for {table_name}: {str(e)}")
            
            results["validations"]["indexes"] = index_validation
            
            if index_validation["issues"]:
                print(f"⚠️  Index issues found: {len(index_validation['issues'])}")
            else:
                print("✅ Index validation passed")
        
        except Exception as e:
            results["errors"].append(f"Index validation failed: {str(e)}")
            print(f"❌ Index validation error: {e}")
    
    async def _validate_constraints(self, results: Dict[str, Any]):
        """Validate database constraints"""
        print("🔒 Validating Constraints...")
        
        constraint_validation = {
            "missing_constraints": [],
            "violated_constraints": [],
            "issues": []
        }
        
        try:
            async with self.session_factory() as session:
                # Check for constraint violations
                constraint_checks = [
                    ("users", "ban_count >= 0", "ck_users_ban_count_non_negative"),
                    ("users", "warn_count >= 0", "ck_users_warn_count_non_negative"),
                    ("groups", "max_warns >= 0", "ck_groups_max_warns_positive"),
                    ("groups", "flood_limit >= 0", "ck_groups_flood_limit_positive"),
                    ("loyalty_points", "points >= 0", "ck_loyalty_points_non_negative"),
                    ("loyalty_points", "total_actions >= 0", "ck_loyalty_actions_non_negative"),
                ]
                
                for table, condition, constraint_name in constraint_checks:
                    try:
                        query = text(f"SELECT COUNT(*) as count FROM {table} WHERE NOT ({condition})")
                        result = await session.execute(query)
                        violation_count = result.scalar()
                        
                        if violation_count > 0:
                            constraint_validation["violated_constraints"].append({
                                "table": table,
                                "constraint": constraint_name,
                                "violations": violation_count
                            })
                            constraint_validation["issues"].append(f"Constraint violation: {constraint_name}")
                    except Exception as e:
                        # Constraint might not exist, which is okay for new tables
                        if "does not exist" not in str(e).lower():
                            constraint_validation["issues"].append(f"Error checking constraint {constraint_name}: {str(e)}")
            
            results["validations"]["constraints"] = constraint_validation
            
            if constraint_validation["issues"]:
                print(f"⚠️  Constraint issues: {len(constraint_validation['issues'])}")
            else:
                print("✅ Constraint validation passed")
        
        except Exception as e:
            results["errors"].append(f"Constraint validation failed: {str(e)}")
            print(f"❌ Constraint validation error: {e}")
    
    async def _test_database_operations(self, results: Dict[str, Any]):
        """Test basic database operations"""
        print("🧪 Testing Database Operations...")
        
        operations_validation = {
            "create_operations": {},
            "read_operations": {},
            "update_operations": {},
            "delete_operations": {},
            "issues": []
        }
        
        try:
            async with self.session_factory() as session:
                # Test basic operations on key tables
                test_tables = ["users", "groups", "warns", "filters"]
                
                for table in test_tables:
                    try:
                        # Test read operation
                        query = text(f"SELECT COUNT(*) as count FROM {table}")
                        result = await session.execute(query)
                        count = result.scalar()
                        operations_validation["read_operations"][table] = {"count": count}
                        
                        # Test basic query performance
                        start_time = datetime.utcnow()
                        query = text(f"SELECT * FROM {table} LIMIT 10")
                        await session.execute(query)
                        end_time = datetime.utcnow()
                        
                        query_time = (end_time - start_time).total_seconds()
                        if query_time > 1.0:  # Slow query
                            operations_validation["issues"].append(f"Slow query on {table}: {query_time:.2f}s")
                    
                    except Exception as e:
                        operations_validation["issues"].append(f"Error testing {table}: {str(e)}")
            
            results["validations"]["operations"] = operations_validation
            
            if operations_validation["issues"]:
                print(f"⚠️  Operation issues: {len(operations_validation['issues'])}")
            else:
                print("✅ Database operations test passed")
        
        except Exception as e:
            results["errors"].append(f"Database operations test failed: {str(e)}")
            print(f"❌ Database operations test error: {e}")
    
    async def _validate_performance_views(self, results: Dict[str, Any]):
        """Validate performance views"""
        print("👁️ Validating Performance Views...")
        
        views_validation = {
            "existing_views": [],
            "missing_views": [],
            "view_errors": [],
            "issues": []
        }
        
        expected_views = ["vw_user_stats", "vw_group_stats", "vw_acn_stats"]
        
        try:
            async with self.engine.begin() as conn:
                inspector = inspect(conn)
                
                # Get existing views
                try:
                    existing_views = inspector.get_view_names()
                    views_validation["existing_views"] = existing_views
                except Exception:
                    existing_views = []
                
                # Check for missing views
                missing_views = set(expected_views) - set(existing_views)
                views_validation["missing_views"] = list(missing_views)
                
                # Test existing views
                for view_name in existing_views:
                    try:
                        query = text(f"SELECT COUNT(*) as count FROM {view_name}")
                        result = await conn.execute(query)
                        count = result.scalar()
                        
                        if count is None:
                            views_validation["view_errors"].append(f"View {view_name} returned NULL count")
                            views_validation["issues"].append(f"View error: {view_name}")
                    except Exception as e:
                        views_validation["view_errors"].append(f"Error testing view {view_name}: {str(e)}")
                        views_validation["issues"].append(f"View test failed: {view_name}")
            
            results["validations"]["performance_views"] = views_validation
            
            if views_validation["issues"]:
                print(f"⚠️  Performance view issues: {len(views_validation['issues'])}")
            else:
                print("✅ Performance views validation passed")
        
        except Exception as e:
            results["errors"].append(f"Performance views validation failed: {str(e)}")
            print(f"❌ Performance views validation error: {e}")
    
    def _generate_summary(self, results: Dict[str, Any]):
        """Generate validation summary"""
        summary = {
            "total_validations": len(results["validations"]),
            "total_errors": len(results["errors"]),
            "total_warnings": len(results["warnings"]),
            "validation_status": "PASSED" if not results["errors"] else "FAILED",
            "critical_issues": [],
            "recommendations": []
        }
        
        # Identify critical issues
        for validation_type, validation_data in results["validations"].items():
            if "issues" in validation_data:
                for issue in validation_data["issues"]:
                    if "Missing" in issue or "orphaned" in issue.lower():
                        summary["critical_issues"].append(issue)
        
        # Generate recommendations
        if results["errors"]:
            summary["recommendations"].append("Fix critical errors before proceeding")
        
        if results["warnings"]:
            summary["recommendations"].append("Review and address warnings")
        
        if not summary["critical_issues"] and not results["errors"]:
            summary["recommendations"].append("Database is ready for production use")
        
        results["summary"] = summary
    
    def print_validation_report(self, results: Dict[str, Any]):
        """Print comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 DATABASE VALIDATION REPORT")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"🎯 Overall Status: {summary['validation_status']}")
        print(f"📋 Validations Run: {summary['total_validations']}")
        print(f"❌ Errors: {summary['total_errors']}")
        print(f"⚠️  Warnings: {summary['total_warnings']}")
        
        if summary["critical_issues"]:
            print(f"\n🚨 Critical Issues ({len(summary['critical_issues'])}):")
            for issue in summary["critical_issues"]:
                print(f"• {issue}")
        
        if results["errors"]:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"• {error}")
        
        if results["warnings"]:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results["warnings"]:
                print(f"• {warning}")
        
        if summary["recommendations"]:
            print(f"\n💡 Recommendations:")
            for recommendation in summary["recommendations"]:
                print(f"• {recommendation}")
        
        print("\n" + "=" * 60)


async def main():
    """Run comprehensive database validation"""
    validator = DatabaseValidator()
    results = await validator.run_comprehensive_validation()
    validator.print_validation_report(results)
    
    # Save results to file
    import json
    with open('database_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Validation results saved to 'database_validation_results.json'")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
