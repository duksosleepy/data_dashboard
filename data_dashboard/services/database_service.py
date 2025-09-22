import os
from pathlib import Path
from typing import Any, Dict, List

import duckdb
import pandas as pd


class DatabaseService:
    """Service layer for DuckDB database operations."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv(
            "DB_PATH", "/home/khoi/code/crm-restate/orders.db"
        )
        self._connection = None

    def get_connection(self):
        """Get or create database connection."""
        if self._connection is None:
            if Path(self.db_path).exists():
                self._connection = duckdb.connect(self.db_path)
            else:
                raise FileNotFoundError(
                    f"Database file not found: {self.db_path}"
                )
        return self._connection

    def close_connection(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def get_orders_data(self) -> List[Dict[str, Any]]:
        """
        Fetch orders data from DuckDB database.
        Returns data formatted for Reflex table consumption.
        """
        try:
            con = self.get_connection()
            query = """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY order_date DESC) as id,
                    CAST(order_date AS VARCHAR) as "order_date",
                    document_type as "document_type",
                    document_number as "document_number",
                    department_code as "department_code",
                    order_id as "order_id",
                    customer_name as "customer_name",
                    phone_number as "phone_number",
                    province as "province",
                    district as "district",
                    ward as "ward",
                    address as "address",
                    product_code as "product_code",
                    product_name as "product_name",
                    imei as "imei",
                    quantity as "quantity",
                    revenue as "revenue",
                    error_code as "error_code",
                    source_type as "source_type"
                FROM orders
                ORDER BY order_date DESC
                LIMIT 1000
            """

            df = con.execute(query).df()

            # Convert DataFrame to list of dictionaries
            records = df.to_dict("records")

            # Ensure all values are JSON serializable and convert id to int
            for record in records:
                for key, value in record.items():
                    if key == "id":
                        # Keep id as integer
                        record[key] = int(value) if value is not None else 0
                    elif pd.isna(value):
                        record[key] = ""
                    elif isinstance(value, (pd.Timestamp, pd.NaT.__class__)):
                        record[key] = str(value) if not pd.isna(value) else ""
                    else:
                        record[key] = str(value) if value is not None else ""

            return records

        except Exception as e:
            print(f"Error fetching orders data: {e}")
            return []

    def get_table_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the orders table."""
        try:
            con = self.get_connection()

            stats_query = """
                SELECT
                    COUNT(*) as total_records,
                    COUNT(DISTINCT customer_name) as unique_customers,
                    COUNT(DISTINCT province) as unique_provinces,
                    SUM(revenue) as total_revenue,
                    MIN(order_date) as earliest_date,
                    MAX(order_date) as latest_date
                FROM orders
            """

            result = con.execute(stats_query).fetchone()

            return {
                "total_records": result[0] if result[0] else 0,
                "unique_customers": result[1] if result[1] else 0,
                "unique_provinces": result[2] if result[2] else 0,
                "total_revenue": float(result[3]) if result[3] else 0.0,
                "earliest_date": str(result[4]) if result[4] else "",
                "latest_date": str(result[5]) if result[5] else "",
            }

        except Exception as e:
            print(f"Error fetching table stats: {e}")
            return {
                "total_records": 0,
                "unique_customers": 0,
                "unique_provinces": 0,
                "total_revenue": 0.0,
                "earliest_date": "",
                "latest_date": "",
            }

    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a specific column."""
        try:
            con = self.get_connection()
            query = f"""
                SELECT DISTINCT {column}
                FROM orders
                WHERE {column} IS NOT NULL AND {column} != ''
                ORDER BY {column}
            """

            result = con.execute(query).fetchall()
            return [str(row[0]) for row in result if row[0] is not None]

        except Exception as e:
            print(f"Error fetching unique values for {column}: {e}")
            return []

    def get_unique_source_types(self) -> List[str]:
        """Get unique source types from orders table."""
        try:
            con = self.get_connection()
            query = """
                SELECT DISTINCT source_type
                FROM orders
                WHERE source_type IS NOT NULL AND source_type != ''
                ORDER BY source_type
            """

            result = con.execute(query).fetchall()
            return [str(row[0]) for row in result if row[0] is not None]

        except Exception as e:
            print(f"Error fetching unique source types: {e}")
            return []

    def get_orders_error_data(self) -> List[Dict[str, Any]]:
        """
        Fetch order_id and error_code data from DuckDB database.
        Returns data formatted for the second table with Vietnamese headers.
        """
        try:
            con = self.get_connection()
            query = """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY order_id) as id,
                    order_id as "order_id",
                    error_code as "error_code"
                FROM orders
                WHERE order_id IS NOT NULL
                ORDER BY order_id
                LIMIT 1000
            """

            df = con.execute(query).df()

            # Convert DataFrame to list of dictionaries
            records = df.to_dict("records")

            # Ensure all values are JSON serializable and convert id to int
            for record in records:
                for key, value in record.items():
                    if key == "id":
                        # Keep id as integer
                        record[key] = int(value) if value is not None else 0
                    elif pd.isna(value):
                        record[key] = ""
                    else:
                        record[key] = str(value) if value is not None else ""

            return records

        except Exception as e:
            print(f"Error fetching orders error data: {e}")
            return []

    def get_daily_task_stats(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Fetch daily task statistics from daily_task_stats table.
        Returns data formatted for the chart with zero-filling for missing days.
        Data is grouped by the created_at field converted to date.
        """
        try:
            con = self.get_connection()

            # Generate date series for the last N days
            query = f"""
                WITH date_series AS (
                    SELECT
                        (CURRENT_DATE - INTERVAL (generate_series) DAY)::DATE as chart_date
                    FROM generate_series(0, {days - 1})
                ),
                stats_data AS (
                    SELECT
                        chart_date,
                        COALESCE(SUM(completed_tasks), 0) as completed_tasks,
                        COALESCE(SUM(failed_tasks), 0) as failed_tasks
                    FROM date_series
                    LEFT JOIN daily_task_stats ON DATE(daily_task_stats.created_at) = chart_date
                    GROUP BY chart_date
                )
                SELECT
                    chart_date,
                    completed_tasks,
                    failed_tasks
                FROM stats_data
                ORDER BY chart_date ASC
            """

            df = con.execute(query).df()

            # Convert to chart format
            records = []
            for _, row in df.iterrows():
                date_obj = pd.to_datetime(row["chart_date"])
                records.append(
                    {
                        "date": date_obj.strftime("%b %d"),
                        "series1": int(row["failed_tasks"])
                        if not pd.isna(row["failed_tasks"])
                        else 0,
                        "series2": int(row["completed_tasks"])
                        if not pd.isna(row["completed_tasks"])
                        else 0,
                    }
                )

            return records

        except Exception as e:
            print(f"Error fetching daily task stats: {e}")
            # Fallback to empty data with proper structure
            import datetime

            today = datetime.date.today()
            records = []
            for i in range(days):
                date = today - datetime.timedelta(days=i)
                records.append(
                    {
                        "date": date.strftime("%b %d"),
                        "series1": 0,
                        "series2": 0,
                    }
                )
            return list(reversed(records))

    def get_monthly_revenue(self, months_ago: int = 0) -> float:
        """Get total revenue for a specific month (0 = current month, 1 = previous month, etc.)."""
        try:
            con = self.get_connection()
            query = f"""
                SELECT COALESCE(SUM(revenue), 0) as total_revenue
                FROM orders
                WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM (CURRENT_DATE - INTERVAL '{months_ago} month'))
                AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM (CURRENT_DATE - INTERVAL '{months_ago} month'))
            """
            result = con.execute(query).fetchone()
            return float(result[0]) if result[0] else 0.0
        except Exception:
            print("Error fetching monthly revenue: {e}")
            return 0.0

    def get_monthly_failed_tasks(self, months_ago: int = 0) -> int:
        """Get total failed tasks for a specific month based on created_at."""
        try:
            con = self.get_connection()
            query = f"""
                SELECT COALESCE(SUM(failed_tasks), 0) as total_failed
                FROM daily_task_stats
                WHERE EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM (CURRENT_DATE - INTERVAL '{months_ago} month'))
                AND EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM (CURRENT_DATE - INTERVAL '{months_ago} month'))
            """
            result = con.execute(query).fetchone()
            return int(result[0]) if result[0] else 0
        except Exception as e:
            print(f"Error fetching monthly failed tasks: {e}")
            return 0

    def get_monthly_completed_tasks(self, months_ago: int = 0) -> int:
        """Get total completed tasks for a specific month based on created_at."""
        try:
            con = self.get_connection()
            query = f"""
                SELECT COALESCE(SUM(completed_tasks), 0) as total_completed
                FROM daily_task_stats
                WHERE EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM (CURRENT_DATE - INTERVAL '{months_ago} month'))
                AND EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM (CURRENT_DATE - INTERVAL '{months_ago} month'))
            """
            result = con.execute(query).fetchone()
            return int(result[0]) if result[0] else 0
        except Exception as e:
            print(f"Error fetching monthly completed tasks: {e}")
            return 0

    def get_non_existing_codes(self) -> List[Dict[str, Any]]:
        """
        Fetch non-existing product codes from the non_existing_codes table.
        Returns data formatted for the product codes table.
        """
        try:
            con = self.get_connection()
            query = """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY product_code) as id,
                    product_code as "product_code"
                FROM non_existing_codes
                WHERE product_code IS NOT NULL AND product_code != ''
                ORDER BY product_code
                LIMIT 500
            """

            df = con.execute(query).df()

            # Convert DataFrame to list of dictionaries
            records = df.to_dict("records")

            # Ensure all values are JSON serializable
            for record in records:
                for key, value in record.items():
                    if key == "id":
                        record[key] = int(value) if value is not None else 0
                    elif pd.isna(value):
                        record[key] = ""
                    else:
                        record[key] = str(value) if value is not None else ""

            return records

        except Exception as e:
            print(f"Error fetching non-existing codes: {e}")
            return []

    def get_orders_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of offline vs online orders based on some criteria.
        This is a placeholder - adjust the logic based on your actual data structure.
        """
        try:
            con = self.get_connection()

            # Assuming online/offline is determined by some field like 'channel' or based on error_code
            # Adjust this query based on your actual data structure
            query = """
                SELECT
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN error_code IS NULL OR error_code = '' THEN 1 END) as online_orders,
                    COUNT(CASE WHEN error_code IS NOT NULL AND error_code != '' THEN 1 END) as offline_orders
                FROM orders
            """

            result = con.execute(query).fetchone()

            total = int(result[0]) if result[0] else 0
            online = int(result[1]) if result[1] else 0
            offline = int(result[2]) if result[2] else 0

            online_percent = (online / total * 100) if total > 0 else 0
            offline_percent = (offline / total * 100) if total > 0 else 0

            return {
                "total_orders": total,
                "online_orders": online,
                "offline_orders": offline,
                "online_percent": round(online_percent, 1),
                "offline_percent": round(offline_percent, 1)
            }

        except Exception as e:
            print(f"Error fetching orders status summary: {e}")
            return {
                "total_orders": 0,
                "online_orders": 0,
                "offline_orders": 0,
                "online_percent": 0.0,
                "offline_percent": 0.0
            }


# Global database service instance
db_service = DatabaseService()
