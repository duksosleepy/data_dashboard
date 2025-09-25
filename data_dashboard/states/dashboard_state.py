import datetime
import io
from typing import (
    List,
    Optional,
    Set,
    TypedDict,
)

import pandas as pd
import reflex as rx
from faker import Faker

from data_dashboard.models.entry import DetailEntry
from data_dashboard.models.order import OrderEntry
from data_dashboard.services.database_service import db_service
from data_dashboard.states.data import raw_data

fake = Faker()


class Metric(TypedDict):
    title: str
    value: str
    change: str
    change_direction: str
    description: str
    trend_description: str


class VisitorDataPoint(TypedDict):
    date: str
    series1: int
    series2: int


class DashboardState(rx.State):
    """Combined state for the data dashboard."""

    selected_section: str = "overview"

    key_metrics: List[Metric] = []
    visitor_data: List[VisitorDataPoint] = []
    displayed_visitor_data: List[VisitorDataPoint] = []
    selected_visitor_timeframe: str = "3 tháng gần nhất"

    _data: List[DetailEntry] = raw_data
    _orders_data: List[OrderEntry] = []
    _orders_error_data: List[dict] = []
    _product_codes_data: List[dict] = []
    orders_status_summary: dict = {}

    # Column names for orders table (Vietnamese headers)
    orders_column_names: List[str] = [
        "Ngày Ct",
        "Mã Ct",
        "Số Ct",
        "Mã bộ phận",
        "Mã đơn hàng",
        "Tên khách hàng",
        "Số điện thoại",
        "Tỉnh thành",
        "Quận huyện",
        "Phường xã",
        "Địa chỉ",
        "Mã hàng",
        "Tên hàng",
        "Imei",
        "Số lượng",
        "Doanh thu",
        "Ghi chú",
        "Nguồn",
        "Edit",
    ]

    # Column names for secondary table (Vietnamese headers for order errors)
    column_names: List[str] = [
        "Mã đơn hàng",
        "Thông báo lỗi",
        "Edit",
    ]
    # Orders table state (for first table)
    orders_search_customer: str = ""
    orders_selected_types: Set[str] = set()
    orders_selected_products: Set[str] = set()
    orders_min_revenue: Optional[float] = None
    orders_max_revenue: Optional[float] = None
    orders_start_date: Optional[str] = None
    orders_end_date: Optional[str] = None
    orders_temp_selected_types: Set[str] = set()
    orders_temp_selected_products: Set[str] = set()
    orders_temp_min_revenue_str: str = ""
    orders_temp_max_revenue_str: str = ""
    orders_temp_start_date: str = ""
    orders_temp_end_date: str = ""
    show_orders_type_filter: bool = False
    show_orders_product_filter: bool = False
    show_orders_revenue_filter: bool = False
    show_orders_date_filter: bool = False
    orders_sort_column: Optional[str] = None
    orders_sort_ascending: bool = True
    orders_selected_rows: Set[int] = set()
    orders_current_page: int = 1
    orders_rows_per_page: int = 20
    show_orders_export_dropdown: bool = False

    # Original data state (for secondary table)
    search_owner: str = ""
    selected_statuses: Set[str] = set()
    selected_regions: Set[str] = set()
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    temp_selected_statuses: Set[str] = set()
    temp_selected_regions: Set[str] = set()
    temp_min_cost_str: str = ""
    temp_max_cost_str: str = ""
    temp_start_date: str = ""
    temp_end_date: str = ""
    show_status_filter: bool = False
    show_region_filter: bool = False
    show_costs_filter: bool = False
    show_date_filter: bool = False
    sort_column: Optional[str] = None
    sort_ascending: bool = True
    selected_rows: Set[int] = set()
    current_page: int = 1
    rows_per_page: int = 20
    show_export_dropdown: bool = False

    # Secondary table state variables
    secondary_search_owner: str = ""
    secondary_selected_statuses: Set[str] = set()
    secondary_selected_regions: Set[str] = set()
    secondary_min_cost: Optional[float] = None
    secondary_max_cost: Optional[float] = None
    secondary_temp_selected_statuses: Set[str] = set()
    secondary_temp_selected_regions: Set[str] = set()
    secondary_temp_min_cost_str: str = ""
    secondary_temp_max_cost_str: str = ""
    show_secondary_status_filter: bool = False
    show_secondary_region_filter: bool = False
    show_secondary_costs_filter: bool = False
    secondary_sort_column: Optional[str] = None
    secondary_sort_ascending: bool = True
    secondary_selected_rows: Set[int] = set()
    secondary_current_page: int = 1
    secondary_rows_per_page: int = 20
    show_secondary_export_dropdown: bool = False

    # Product codes table state variables
    product_codes_current_page: int = 1
    product_codes_rows_per_page: int = 15

    @rx.var
    def has_status_filter(self) -> bool:
        """Check if status filter is active."""
        return len(self.selected_statuses) > 0

    @rx.var
    def has_region_filter(self) -> bool:
        """Check if region filter is active."""
        return len(self.selected_regions) > 0

    @rx.var
    def has_costs_filter(self) -> bool:
        """Check if costs filter is active."""
        return self.min_cost is not None or self.max_cost is not None

    @rx.var
    def unique_statuses(self) -> List[str]:
        """Get unique statuses from the data."""
        return sorted({item["status"] for item in self._data})

    @rx.var
    def unique_regions(self) -> List[str]:
        """Get unique regions from the data."""
        return sorted({item["region"] for item in self._data})

    # Orders table computed properties
    @rx.var
    def unique_types(self) -> List[str]:
        """Get unique source types from orders data."""
        return sorted(
            {item["source_type"] for item in self._orders_data if item["source_type"]}
        )

    @rx.var
    def unique_products(self) -> List[str]:
        """Get unique product names from orders data."""
        return sorted(
            {
                item["product_name"]
                for item in self._orders_data
                if item["product_name"]
            }
        )

    @rx.var
    def orders_filtered_data(self) -> List[OrderEntry]:
        """Filter the orders data based on current filter selections."""
        data = self._orders_data
        if self.orders_search_customer:
            data = [
                item
                for item in data
                if self.orders_search_customer.lower()
                in item["customer_name"].lower()
            ]
        if self.orders_selected_types:
            data = [
                item
                for item in data
                if item["source_type"] in self.orders_selected_types
            ]
        if self.orders_selected_products:
            data = [
                item
                for item in data
                if item["product_name"] in self.orders_selected_products
            ]
        if self.orders_min_revenue is not None:
            data = [
                item
                for item in data
                if float(item["revenue"] or 0) >= self.orders_min_revenue
            ]
        if self.orders_max_revenue is not None:
            data = [
                item
                for item in data
                if float(item["revenue"] or 0) <= self.orders_max_revenue
            ]
        if self.orders_start_date is not None:
            data = [
                item
                for item in data
                if item["order_date"] and item["order_date"] >= self.orders_start_date
            ]
        if self.orders_end_date is not None:
            data = [
                item
                for item in data
                if item["order_date"] and item["order_date"] <= self.orders_end_date
            ]
        return data

    @rx.var
    def orders_filtered_and_sorted_data(self) -> List[OrderEntry]:
        """Sort the orders filtered data."""
        data_to_sort = self.orders_filtered_data
        if self.orders_sort_column:
            try:
                sort_key_map = {
                    "Ngày Ct": "order_date",
                    "Mã Ct": "document_type",
                    "Số Ct": "document_number",
                    "Mã bộ phận": "department_code",
                    "Mã đơn hàng": "order_id",
                    "Tên khách hàng": "customer_name",
                    "Số điện thoại": "phone_number",
                    "Tỉnh thành": "province",
                    "Quận huyện": "district",
                    "Phường xã": "ward",
                    "Địa chỉ": "address",
                    "Mã hàng": "product_code",
                    "Tên hàng": "product_name",
                    "Imei": "imei",
                    "Số lượng": "quantity",
                    "Doanh thu": "revenue",
                    "Ghi chú": "error_code",
                }
                internal_key = sort_key_map.get(self.orders_sort_column)
                if internal_key:
                    if internal_key in ["revenue", "quantity"]:

                        def key_func(item):
                            return float(item[internal_key] or 0)
                    else:

                        def key_func(item):
                            return item[internal_key] or ""

                    data_to_sort = sorted(
                        data_to_sort,
                        key=key_func,
                        reverse=not self.orders_sort_ascending,
                    )
                else:
                    pass
            except (KeyError, ValueError):
                pass
        return data_to_sort

    @rx.var
    def orders_total_rows(self) -> int:
        """Total number of rows after filtering for orders table."""
        return len(self.orders_filtered_and_sorted_data)

    @rx.var
    def orders_total_pages(self) -> int:
        """Total number of pages for orders table."""
        if self.orders_rows_per_page <= 0:
            return 1
        return (
            (self.orders_total_rows + self.orders_rows_per_page - 1)
            // self.orders_rows_per_page
            if self.orders_rows_per_page > 0
            else 1
        )

    @rx.var
    def orders_paginated_data(self) -> List[OrderEntry]:
        """Get the data for the current page of orders table."""
        start_index = (self.orders_current_page - 1) * self.orders_rows_per_page
        end_index = start_index + self.orders_rows_per_page
        return self.orders_filtered_and_sorted_data[start_index:end_index]

    @rx.var
    def orders_current_rows_display(self) -> str:
        """Display string for current rows in orders table."""
        if self.orders_total_rows == 0:
            return "0"
        start = (self.orders_current_page - 1) * self.orders_rows_per_page + 1
        end = min(
            self.orders_current_page * self.orders_rows_per_page,
            self.orders_total_rows,
        )
        return f"{start}-{end}"

    @rx.var
    def orders_page_item_ids(self) -> Set[int]:
        """Get the set of IDs for items on the current page of orders table."""
        return {item["id"] for item in self.orders_paginated_data}

    @rx.var
    def orders_all_rows_on_page_selected(self) -> bool:
        """Check if all rows on the current page are selected in orders table."""
        if not self.orders_paginated_data:
            return False
        return self.orders_page_item_ids.issubset(self.orders_selected_rows)

    @rx.var
    def total_revenue(self) -> float:
        """Calculate total revenue from orders data."""
        if not self._orders_data:
            return 0.0
        return sum(
            float(item.get("revenue", 0) or 0) for item in self._orders_data
        )

    @rx.var
    def total_failed_tasks(self) -> int:
        """Calculate total failed tasks from daily_task_stats."""
        if not self.visitor_data:
            return 0
        return sum(item.get("series1", 0) for item in self.visitor_data)

    @rx.var
    def total_completed_tasks(self) -> int:
        """Calculate total completed tasks from daily_task_stats."""
        if not self.visitor_data:
            return 0
        return sum(item.get("series2", 0) for item in self.visitor_data)

    @rx.var
    def revenue_change_percent(self) -> tuple[float, str]:
        """Calculate revenue change between current and previous month."""
        try:
            # Get current and previous month data from database
            current_month_revenue = db_service.get_monthly_revenue(0)  # Current month
            previous_month_revenue = db_service.get_monthly_revenue(1)  # Previous month

            if previous_month_revenue == 0:
                return (0.0, "neutral")

            change = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
            direction = "up" if change > 0 else "down" if change < 0 else "neutral"
            return (change, direction)
        except Exception:
            return (0.0, "neutral")

    @rx.var
    def failed_tasks_change_percent(self) -> tuple[float, str]:
        """Calculate failed tasks change between current and previous month."""
        try:
            current_month_failed = db_service.get_monthly_failed_tasks(0)  # Current month
            previous_month_failed = db_service.get_monthly_failed_tasks(1)  # Previous month

            if previous_month_failed == 0:
                return (0.0, "neutral")

            change = ((current_month_failed - previous_month_failed) / previous_month_failed) * 100
            direction = "up" if change > 0 else "down" if change < 0 else "neutral"
            return (change, direction)
        except Exception:
            return (0.0, "neutral")

    @rx.var
    def completed_tasks_change_percent(self) -> tuple[float, str]:
        """Calculate completed tasks change between current and previous month."""
        try:
            current_month_completed = db_service.get_monthly_completed_tasks(0)  # Current month
            previous_month_completed = db_service.get_monthly_completed_tasks(1)  # Previous month

            if previous_month_completed == 0:
                return (0.0, "neutral")

            change = ((current_month_completed - previous_month_completed) / previous_month_completed) * 100
            direction = "up" if change > 0 else "down" if change < 0 else "neutral"
            return (change, direction)
        except Exception:
            return (0.0, "neutral")

    @rx.var
    def filtered_data(self) -> List[DetailEntry]:
        """Filter the data based on current filter selections."""
        data = self._data
        if self.search_owner:
            data = [
                item
                for item in data
                if self.search_owner.lower() in item["owner"].lower()
            ]
        if self.selected_statuses:
            data = [
                item
                for item in data
                if item["status"] in self.selected_statuses
            ]
        if self.selected_regions:
            data = [
                item for item in data if item["region"] in self.selected_regions
            ]
        if self.min_cost is not None:
            data = [item for item in data if item["costs"] >= self.min_cost]
        if self.max_cost is not None:
            data = [item for item in data if item["costs"] <= self.max_cost]
        if self.start_date is not None:
            data = [
                item
                for item in data
                if item["last_edited"] and self._parse_date_for_comparison(item["last_edited"]) >= self.start_date
            ]
        if self.end_date is not None:
            data = [
                item
                for item in data
                if item["last_edited"] and self._parse_date_for_comparison(item["last_edited"]) <= self.end_date
            ]
        return data

    def _parse_date_for_comparison(self, date_str: str) -> str:
        """Parse the date string from 'DD/MM/YYYY HH:MM' format to 'YYYY-MM-DD' for comparison."""
        try:
            date_part = date_str.split(' ')[0]  # Get just the date part
            day, month, year = date_part.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except (ValueError, IndexError):
            return "1900-01-01"  # Fallback date

    @rx.var
    def filtered_and_sorted_data(self) -> List[DetailEntry]:
        """Sort the filtered data."""
        data_to_sort = self.filtered_data
        if self.sort_column:
            try:
                sort_key_map = {
                    "Owner": "owner",
                    "Status": "status",
                    "Region": "region",
                    "Stability": "stability",
                    "Costs": "costs",
                    "Last edited": "last_edited",
                }
                internal_key = sort_key_map.get(self.sort_column)
                if internal_key:
                    if self.sort_column == "Last edited":

                        def key_func(item):
                            return datetime.datetime.strptime(
                                item[internal_key],
                                "%d/%m/%Y %H:%M",
                            )
                    else:

                        def key_func(item):
                            return item[internal_key]

                    data_to_sort = sorted(
                        data_to_sort,
                        key=key_func,
                        reverse=not self.sort_ascending,
                    )
                else:
                    pass
            except KeyError:
                pass
            except ValueError:
                pass
        return data_to_sort

    @rx.var
    def total_rows(self) -> int:
        """Total number of rows after filtering."""
        return len(self.filtered_and_sorted_data)

    @rx.var
    def total_pages(self) -> int:
        """Total number of pages."""
        if self.rows_per_page <= 0:
            return 1
        return (
            (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
            if self.rows_per_page > 0
            else 1
        )

    @rx.var
    def paginated_data(self) -> List[DetailEntry]:
        """Get the data for the current page."""
        start_index = (self.current_page - 1) * self.rows_per_page
        end_index = start_index + self.rows_per_page
        return self.filtered_and_sorted_data[start_index:end_index]

    @rx.var
    def current_rows_display(self) -> str:
        """Display string for current rows."""
        if self.total_rows == 0:
            return "0"
        start = (self.current_page - 1) * self.rows_per_page + 1
        end = min(
            self.current_page * self.rows_per_page,
            self.total_rows,
        )
        return f"{start}-{end}"

    @rx.var
    def page_item_ids(self) -> Set[int]:
        """Get the set of IDs for items on the current page."""
        return {item["id"] for item in self.paginated_data}

    @rx.var
    def all_rows_on_page_selected(self) -> bool:
        """Check if all rows on the current page are selected."""
        if not self.paginated_data:
            return False
        return self.page_item_ids.issubset(self.selected_rows)

    # Secondary table computed properties
    @rx.var
    def secondary_filtered_data(self) -> List[dict]:
        """Filter the secondary data based on current filter selections."""
        data = self._orders_error_data
        if self.secondary_search_owner:
            data = [
                item
                for item in data
                if self.secondary_search_owner.lower()
                in item["order_id"].lower()
            ]
        return data

    @rx.var
    def secondary_filtered_and_sorted_data(self) -> List[dict]:
        """Sort the secondary filtered data."""
        data_to_sort = self.secondary_filtered_data
        if self.secondary_sort_column:
            try:
                sort_key_map = {
                    "Mã đơn hàng": "order_id",
                    "Thông báo lỗi": "error_code",
                }
                internal_key = sort_key_map.get(self.secondary_sort_column)
                if internal_key:

                    def key_func(item):
                        return item[internal_key] or ""

                    data_to_sort = sorted(
                        data_to_sort,
                        key=key_func,
                        reverse=not self.secondary_sort_ascending,
                    )
                else:
                    pass
            except KeyError:
                pass
            except ValueError:
                pass
        return data_to_sort

    @rx.var
    def secondary_total_rows(self) -> int:
        """Total number of rows after filtering for secondary table."""
        return len(self.secondary_filtered_and_sorted_data)

    @rx.var
    def secondary_total_pages(self) -> int:
        """Total number of pages for secondary table."""
        if self.secondary_rows_per_page <= 0:
            return 1
        return (
            (self.secondary_total_rows + self.secondary_rows_per_page - 1)
            // self.secondary_rows_per_page
            if self.secondary_rows_per_page > 0
            else 1
        )

    @rx.var
    def secondary_paginated_data(self) -> List[dict]:
        """Get the data for the current page of secondary table."""
        start_index = (
            self.secondary_current_page - 1
        ) * self.secondary_rows_per_page
        end_index = start_index + self.secondary_rows_per_page
        return self.secondary_filtered_and_sorted_data[start_index:end_index]

    @rx.var
    def secondary_current_rows_display(self) -> str:
        """Display string for current rows in secondary table."""
        if self.secondary_total_rows == 0:
            return "0"
        start = (
            self.secondary_current_page - 1
        ) * self.secondary_rows_per_page + 1
        end = min(
            self.secondary_current_page * self.secondary_rows_per_page,
            self.secondary_total_rows,
        )
        return f"{start}-{end}"

    @rx.var
    def secondary_page_item_ids(self) -> Set[int]:
        """Get the set of IDs for items on the current page of secondary table."""
        return {item["id"] for item in self.secondary_paginated_data}

    @rx.var
    def secondary_all_rows_on_page_selected(self) -> bool:
        """Check if all rows on the current page are selected in secondary table."""
        if not self.secondary_paginated_data:
            return False
        return self.secondary_page_item_ids.issubset(
            self.secondary_selected_rows
        )

    # Product codes table computed properties
    @rx.var
    def product_codes_total_rows(self) -> int:
        """Total number of product codes."""
        return len(self._product_codes_data)

    @rx.var
    def product_codes_total_pages(self) -> int:
        """Total number of pages for product codes table."""
        if self.product_codes_rows_per_page <= 0:
            return 1
        return (
            (self.product_codes_total_rows + self.product_codes_rows_per_page - 1)
            // self.product_codes_rows_per_page
            if self.product_codes_rows_per_page > 0
            else 1
        )

    @rx.var
    def product_codes_paginated_data(self) -> List[dict]:
        """Get the data for the current page of product codes table."""
        start_index = (self.product_codes_current_page - 1) * self.product_codes_rows_per_page
        end_index = start_index + self.product_codes_rows_per_page
        return self._product_codes_data[start_index:end_index]

    def _generate_fake_data(self):
        """Generates metrics data with real monthly comparisons."""
        revenue_change, revenue_direction = self.revenue_change_percent
        failed_change, failed_direction = self.failed_tasks_change_percent
        completed_change, completed_direction = self.completed_tasks_change_percent

        self.key_metrics = [
            {
                "title": "Tổng doanh thu",
                "value": f"{self.total_revenue:,.0f} VNĐ",
                "change": f"{'+' if revenue_change > 0 else ''}{revenue_change:.1f}%",
                "change_direction": revenue_direction,
                "description": f"{'Tăng' if revenue_change > 0 else 'Giảm' if revenue_change < 0 else 'Không đổi'} so với tháng trước",
                "trend_description": "",
            },
            {
                "title": "Tổng đơn hàng lỗi",
                "value": f"{self.total_failed_tasks:,}",
                "change": f"{'+' if failed_change > 0 else ''}{failed_change:.1f}%",
                "change_direction": failed_direction,
                "description": f"{'Tăng' if failed_change > 0 else 'Giảm' if failed_change < 0 else 'Không đổi'} so với tháng trước",
                "trend_description": "",
            },
            {
                "title": "Tổng đơn hàng thành công",
                "value": f"{self.total_completed_tasks:,}",
                "change": f"{'+' if completed_change > 0 else ''}{completed_change:.1f}%",
                "change_direction": completed_direction,
                "description": f"{'Tăng' if completed_change > 0 else 'Giảm' if completed_change < 0 else 'Không đổi'} so với tháng trước",
                "trend_description": "",
            },
        ]

    def load_chart_data(self):
        """Load chart data from daily_task_stats table."""
        try:
            # Load real data from daily_task_stats
            self.visitor_data = db_service.get_daily_task_stats(90)
            self.displayed_visitor_data = self.visitor_data
        except Exception as e:
            print(f"Error loading chart data: {e}")
            # Fallback to empty data
            today = datetime.date.today()
            self.visitor_data = []
            for i in range(90):
                date = today - datetime.timedelta(days=i)
                self.visitor_data.append(
                    {
                        "date": date.strftime("%b %d"),
                        "series1": 0,
                        "series2": 0,
                    }
                )
            self.visitor_data.reverse()
            self.displayed_visitor_data = self.visitor_data

    def load_orders_data(self):
        """Load orders data from DuckDB."""
        try:
            self._orders_data = db_service.get_orders_data()
            self._orders_error_data = db_service.get_orders_error_data()
            self._product_codes_data = db_service.get_non_existing_codes()
            self.orders_status_summary = db_service.get_orders_status_summary()
        except Exception as e:
            print(f"Error loading orders data: {e}")
            self._orders_data = []
            self._orders_error_data = []
            self._product_codes_data = []
            self.orders_status_summary = {
                "total_orders": 0,
                "online_orders": 0,
                "offline_orders": 0,
                "online_percent": 0.0,
                "offline_percent": 0.0
            }

    @rx.event
    def load_initial_data(self):
        """Load initial data and orders data if not already loaded."""
        if not self._orders_data:
            self.load_orders_data()
        if not self.visitor_data:
            self.load_chart_data()
        if not self.key_metrics:
            self._generate_fake_data()

    @rx.event
    def set_selected_section(self, section: str):
        """Set the selected sidebar section."""
        self.selected_section = section

    @rx.event
    def set_visitor_timeframe(self, timeframe: str):
        self.selected_visitor_timeframe = timeframe

        if timeframe == "3 tháng gần nhất":
            try:
                self.visitor_data = db_service.get_daily_task_stats(90)
                self.displayed_visitor_data = self.visitor_data
            except Exception:
                self.displayed_visitor_data = self.visitor_data

        if timeframe == "30 ngày gần nhất":
            try:
                self.visitor_data = db_service.get_daily_task_stats(30)
                self.displayed_visitor_data = self.visitor_data
            except Exception:
                self.displayed_visitor_data = (
                    self.visitor_data[-30:]
                    if len(self.visitor_data) >= 30
                    else self.visitor_data
                )

        if timeframe == "7 ngày gần nhất":
            try:
                self.visitor_data = db_service.get_daily_task_stats(7)
                self.displayed_visitor_data = self.visitor_data
            except Exception:
                self.displayed_visitor_data = (
                    self.visitor_data[-7:]
                    if len(self.visitor_data) >= 7
                    else self.visitor_data
                )

    @rx.event
    def refresh_all_data(self):
        """Refresh all data - regenerate metrics and reload table data."""
        self.load_orders_data()
        self.load_chart_data()
        self._generate_fake_data()
        self.selected_rows = set()
        self.current_page = 1

    def set_search_owner(self, value: str):
        """Update the search owner filter."""
        self.search_owner = value
        self.current_page = 1

    def toggle_sort(self, column_name: str):
        """Toggle sorting for a column."""
        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column_name
            self.sort_ascending = True

    def go_to_page(self, page_number: int):
        """Navigate to a specific page."""
        if 1 <= page_number <= self.total_pages:
            self.current_page = page_number

    def next_page(self):
        """Go to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1

    def previous_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1

    def toggle_row_selection(self, row_id: int):
        """Toggle selection state for a single row using its ID."""
        if row_id in self.selected_rows:
            self.selected_rows.remove(row_id)
        else:
            self.selected_rows.add(row_id)

    def toggle_select_all_on_page(self):
        """Select or deselect all rows on the current page."""
        page_ids = self.page_item_ids
        if self.all_rows_on_page_selected:
            self.selected_rows -= page_ids
        else:
            self.selected_rows.update(page_ids)

    def toggle_status_filter(self):
        is_opening = not self.show_status_filter
        self.show_status_filter = is_opening
        self.show_region_filter = False
        self.show_costs_filter = False
        self.show_date_filter = False
        if is_opening:
            self.temp_selected_statuses = self.selected_statuses.copy()

    def toggle_region_filter(self):
        is_opening = not self.show_region_filter
        self.show_region_filter = is_opening
        self.show_status_filter = False
        self.show_costs_filter = False
        self.show_date_filter = False
        if is_opening:
            self.temp_selected_regions = self.selected_regions.copy()

    def toggle_costs_filter(self):
        is_opening = not self.show_costs_filter
        self.show_costs_filter = is_opening
        self.show_status_filter = False
        self.show_region_filter = False
        self.show_date_filter = False
        if is_opening:
            self.temp_min_cost_str = (
                str(self.min_cost) if self.min_cost is not None else ""
            )
            self.temp_max_cost_str = (
                str(self.max_cost) if self.max_cost is not None else ""
            )

    def toggle_date_filter(self):
        is_opening = not self.show_date_filter
        self.show_date_filter = is_opening
        self.show_status_filter = False
        self.show_region_filter = False
        self.show_costs_filter = False
        if is_opening:
            self.temp_start_date = (
                self.start_date if self.start_date is not None else ""
            )
            self.temp_end_date = (
                self.end_date if self.end_date is not None else ""
            )

    def toggle_temp_status(self, status: str):
        if status in self.temp_selected_statuses:
            self.temp_selected_statuses.remove(status)
        else:
            self.temp_selected_statuses.add(status)

    def toggle_temp_region(self, region: str):
        if region in self.temp_selected_regions:
            self.temp_selected_regions.remove(region)
        else:
            self.temp_selected_regions.add(region)

    def set_temp_min_cost(self, value: str):
        self.temp_min_cost_str = value

    def set_temp_max_cost(self, value: str):
        self.temp_max_cost_str = value

    def set_temp_start_date(self, value: str):
        self.temp_start_date = value

    def set_temp_end_date(self, value: str):
        self.temp_end_date = value

    def apply_status_filter(self):
        self.selected_statuses = self.temp_selected_statuses.copy()
        self.show_status_filter = False
        self.current_page = 1

    def apply_region_filter(self):
        self.selected_regions = self.temp_selected_regions.copy()
        self.show_region_filter = False
        self.current_page = 1

    def apply_costs_filter(self):
        new_min_cost = None
        new_max_cost = None
        try:
            if self.temp_min_cost_str:
                new_min_cost = float(self.temp_min_cost_str)
        except ValueError:
            pass
        try:
            if self.temp_max_cost_str:
                new_max_cost = float(self.temp_max_cost_str)
        except ValueError:
            pass
        self.min_cost = new_min_cost
        self.max_cost = new_max_cost
        self.show_costs_filter = False
        self.current_page = 1

    def reset_status_filter(self):
        self.temp_selected_statuses = set()
        self.selected_statuses = set()
        self.show_status_filter = False
        self.current_page = 1

    def reset_region_filter(self):
        self.temp_selected_regions = set()
        self.selected_regions = set()
        self.show_region_filter = False
        self.current_page = 1

    def reset_costs_filter(self):
        self.temp_min_cost_str = ""
        self.temp_max_cost_str = ""
        self.min_cost = None
        self.max_cost = None
        self.show_costs_filter = False
        self.current_page = 1

    def apply_date_filter(self):
        self.start_date = (
            self.temp_start_date if self.temp_start_date else None
        )
        self.end_date = (
            self.temp_end_date if self.temp_end_date else None
        )
        self.show_date_filter = False
        self.current_page = 1

    def reset_date_filter(self):
        self.temp_start_date = ""
        self.temp_end_date = ""
        self.start_date = None
        self.end_date = None
        self.show_date_filter = False
        self.current_page = 1

    def reset_all_filters(self):
        """Reset all filters and search."""
        self.search_owner = ""
        self.selected_statuses = set()
        self.selected_regions = set()
        self.min_cost = None
        self.max_cost = None
        self.start_date = None
        self.end_date = None
        self.temp_selected_statuses = set()
        self.temp_selected_regions = set()
        self.temp_min_cost_str = ""
        self.temp_max_cost_str = ""
        self.temp_start_date = ""
        self.temp_end_date = ""
        self.show_status_filter = False
        self.show_region_filter = False
        self.show_costs_filter = False
        self.show_date_filter = False
        self.current_page = 1
        self.selected_rows = set()
        self.sort_column = None
        self.sort_ascending = True

    def close_filter_dropdowns(self):
        self.show_status_filter = False
        self.show_region_filter = False
        self.show_costs_filter = False


    def toggle_export_dropdown(self):
        """Toggle the export dropdown for main table."""
        # Close other export dropdowns first
        self.show_orders_export_dropdown = False
        self.show_secondary_export_dropdown = False
        # Toggle this dropdown
        self.show_export_dropdown = not self.show_export_dropdown

    @rx.event
    def download_csv(self):
        """Download the data as CSV - selected rows if any are selected, otherwise all filtered data."""
        # If rows are selected, export only selected rows, otherwise export all filtered data
        if self.selected_rows:
            data_to_export = [
                item for item in self.filtered_and_sorted_data
                if item["id"] in self.selected_rows
            ]
        else:
            data_to_export = self.filtered_and_sorted_data

        df = pd.DataFrame(data_to_export)
        display_columns = [
            col.lower().replace(" ", "_")
            for col in self.column_names
            if col != "Edit"
        ]
        if "last_edited" not in df.columns and "last_edited" in display_columns:
            display_columns.remove("last_edited")
        if "costs" in df.columns and "costs" in display_columns:
            pass
        column_mapping = {
            "owner": "Owner",
            "status": "Status",
            "region": "Region",
            "stability": "Stability",
            "costs": "Costs",
            "last_edited": "Last edited",
        }
        df_display = df[[key for key in column_mapping if key in df.columns]]
        df_display.columns = [column_mapping[col] for col in df_display.columns]
        stream = io.StringIO()
        df_display.to_csv(stream, index=False)
        return rx.download(
            data=stream.getvalue(),
            filename="details_export.csv",
        )

    @rx.event
    def download_xlsx(self):
        """Download the data as XLSX - selected rows if any are selected, otherwise all filtered data."""
        # If rows are selected, export only selected rows, otherwise export all filtered data
        if self.selected_rows:
            data_to_export = [
                item for item in self.filtered_and_sorted_data
                if item["id"] in self.selected_rows
            ]
        else:
            data_to_export = self.filtered_and_sorted_data

        df = pd.DataFrame(data_to_export)
        display_columns = [
            col.lower().replace(" ", "_")
            for col in self.column_names
            if col != "Edit"
        ]
        if "last_edited" not in df.columns and "last_edited" in display_columns:
            display_columns.remove("last_edited")
        if "costs" in df.columns and "costs" in display_columns:
            pass
        column_mapping = {
            "owner": "Owner",
            "status": "Status",
            "region": "Region",
            "stability": "Stability",
            "costs": "Costs",
            "last_edited": "Last edited",
        }
        df_display = df[[key for key in column_mapping if key in df.columns]]
        df_display.columns = [column_mapping[col] for col in df_display.columns]
        stream = io.BytesIO()
        df_display.to_excel(stream, index=False, engine='openpyxl')
        return rx.download(
            data=stream.getvalue(),
            filename="details_export.xlsx",
        )

    # Secondary table methods
    def set_secondary_search_owner(self, value: str):
        """Update the secondary search owner filter."""
        self.secondary_search_owner = value
        self.secondary_current_page = 1

    def toggle_secondary_sort(self, column_name: str):
        """Toggle sorting for a column in secondary table."""
        if self.secondary_sort_column == column_name:
            self.secondary_sort_ascending = not self.secondary_sort_ascending
        else:
            self.secondary_sort_column = column_name
            self.secondary_sort_ascending = True

    def secondary_go_to_page(self, page_number: int):
        """Navigate to a specific page in secondary table."""
        if 1 <= page_number <= self.secondary_total_pages:
            self.secondary_current_page = page_number

    def secondary_next_page(self):
        """Go to the next page in secondary table."""
        if self.secondary_current_page < self.secondary_total_pages:
            self.secondary_current_page += 1

    def secondary_previous_page(self):
        """Go to the previous page in secondary table."""
        if self.secondary_current_page > 1:
            self.secondary_current_page -= 1

    def toggle_secondary_row_selection(self, row_id: int):
        """Toggle selection state for a single row using its ID in secondary table."""
        if row_id in self.secondary_selected_rows:
            self.secondary_selected_rows.remove(row_id)
        else:
            self.secondary_selected_rows.add(row_id)

    def toggle_secondary_select_all_on_page(self):
        """Select or deselect all rows on the current page in secondary table."""
        page_ids = self.secondary_page_item_ids
        if self.secondary_all_rows_on_page_selected:
            self.secondary_selected_rows -= page_ids
        else:
            self.secondary_selected_rows.update(page_ids)

    def toggle_secondary_status_filter(self):
        is_opening = not self.show_secondary_status_filter
        self.show_secondary_status_filter = is_opening
        self.show_secondary_region_filter = False
        self.show_secondary_costs_filter = False
        if is_opening:
            self.secondary_temp_selected_statuses = (
                self.secondary_selected_statuses.copy()
            )

    def toggle_secondary_region_filter(self):
        is_opening = not self.show_secondary_region_filter
        self.show_secondary_region_filter = is_opening
        self.show_secondary_status_filter = False
        self.show_secondary_costs_filter = False
        if is_opening:
            self.secondary_temp_selected_regions = (
                self.secondary_selected_regions.copy()
            )

    def toggle_secondary_costs_filter(self):
        is_opening = not self.show_secondary_costs_filter
        self.show_secondary_costs_filter = is_opening
        self.show_secondary_status_filter = False
        self.show_secondary_region_filter = False
        if is_opening:
            self.secondary_temp_min_cost_str = (
                str(self.secondary_min_cost)
                if self.secondary_min_cost is not None
                else ""
            )
            self.secondary_temp_max_cost_str = (
                str(self.secondary_max_cost)
                if self.secondary_max_cost is not None
                else ""
            )

    def toggle_secondary_temp_status(self, status: str):
        if status in self.secondary_temp_selected_statuses:
            self.secondary_temp_selected_statuses.remove(status)
        else:
            self.secondary_temp_selected_statuses.add(status)

    def toggle_secondary_temp_region(self, region: str):
        if region in self.secondary_temp_selected_regions:
            self.secondary_temp_selected_regions.remove(region)
        else:
            self.secondary_temp_selected_regions.add(region)

    def set_secondary_temp_min_cost(self, value: str):
        self.secondary_temp_min_cost_str = value

    def set_secondary_temp_max_cost(self, value: str):
        self.secondary_temp_max_cost_str = value

    def apply_secondary_status_filter(self):
        self.secondary_selected_statuses = (
            self.secondary_temp_selected_statuses.copy()
        )
        self.show_secondary_status_filter = False
        self.secondary_current_page = 1

    def apply_secondary_region_filter(self):
        self.secondary_selected_regions = (
            self.secondary_temp_selected_regions.copy()
        )
        self.show_secondary_region_filter = False
        self.secondary_current_page = 1

    def apply_secondary_costs_filter(self):
        new_min_cost = None
        new_max_cost = None
        try:
            if self.secondary_temp_min_cost_str:
                new_min_cost = float(self.secondary_temp_min_cost_str)
        except ValueError:
            pass
        try:
            if self.secondary_temp_max_cost_str:
                new_max_cost = float(self.secondary_temp_max_cost_str)
        except ValueError:
            pass
        self.secondary_min_cost = new_min_cost
        self.secondary_max_cost = new_max_cost
        self.show_secondary_costs_filter = False
        self.secondary_current_page = 1

    def reset_secondary_status_filter(self):
        self.secondary_temp_selected_statuses = set()
        self.secondary_selected_statuses = set()
        self.show_secondary_status_filter = False
        self.secondary_current_page = 1

    def reset_secondary_region_filter(self):
        self.secondary_temp_selected_regions = set()
        self.secondary_selected_regions = set()
        self.show_secondary_region_filter = False
        self.secondary_current_page = 1

    def reset_secondary_costs_filter(self):
        self.secondary_temp_min_cost_str = ""
        self.secondary_temp_max_cost_str = ""
        self.secondary_min_cost = None
        self.secondary_max_cost = None
        self.show_secondary_costs_filter = False
        self.secondary_current_page = 1

    def reset_all_secondary_filters(self):
        """Reset all secondary filters and search."""
        self.secondary_search_owner = ""
        self.secondary_selected_statuses = set()
        self.secondary_selected_regions = set()
        self.secondary_min_cost = None
        self.secondary_max_cost = None
        self.secondary_temp_selected_statuses = set()
        self.secondary_temp_selected_regions = set()
        self.secondary_temp_min_cost_str = ""
        self.secondary_temp_max_cost_str = ""
        self.show_secondary_status_filter = False
        self.show_secondary_region_filter = False
        self.show_secondary_costs_filter = False
        self.secondary_current_page = 1
        self.secondary_selected_rows = set()
        self.secondary_sort_column = None
        self.secondary_sort_ascending = True

    def refresh_secondary_data(self):
        """Refresh secondary data - regenerate metrics and reload table data."""
        self.secondary_selected_rows = set()
        self.secondary_current_page = 1

    def toggle_secondary_export_dropdown(self):
        """Toggle the export dropdown for secondary table."""
        # Close other export dropdowns first
        self.show_export_dropdown = False
        self.show_orders_export_dropdown = False
        # Toggle this dropdown
        self.show_secondary_export_dropdown = not self.show_secondary_export_dropdown

    @rx.event
    def download_secondary_csv(self):
        """Download the secondary data as CSV - selected rows if any are selected, otherwise all filtered data."""
        # If rows are selected, export only selected rows, otherwise export all filtered data
        if self.secondary_selected_rows:
            data_to_export = [
                item for item in self.secondary_filtered_and_sorted_data
                if item["id"] in self.secondary_selected_rows
            ]
        else:
            data_to_export = self.secondary_filtered_and_sorted_data

        df = pd.DataFrame(data_to_export)
        display_columns = [
            col.lower().replace(" ", "_")
            for col in self.column_names
            if col != "Edit"
        ]
        if "last_edited" not in df.columns and "last_edited" in display_columns:
            display_columns.remove("last_edited")
        if "costs" in df.columns and "costs" in display_columns:
            pass
        column_mapping = {
            "order_id": "Mã đơn hàng",
            "error_code": "Thông báo lỗi",
        }
        df_display = df[[key for key in column_mapping if key in df.columns]]
        df_display.columns = [column_mapping[col] for col in df_display.columns]
        stream = io.StringIO()
        df_display.to_csv(stream, index=False)
        return rx.download(
            data=stream.getvalue(),
            filename="secondary_details_export.csv",
        )

    @rx.event
    def download_secondary_xlsx(self):
        """Download the secondary data as XLSX - selected rows if any are selected, otherwise all filtered data."""
        # If rows are selected, export only selected rows, otherwise export all filtered data
        if self.secondary_selected_rows:
            data_to_export = [
                item for item in self.secondary_filtered_and_sorted_data
                if item["id"] in self.secondary_selected_rows
            ]
        else:
            data_to_export = self.secondary_filtered_and_sorted_data

        df = pd.DataFrame(data_to_export)
        display_columns = [
            col.lower().replace(" ", "_")
            for col in self.column_names
            if col != "Edit"
        ]
        if "last_edited" not in df.columns and "last_edited" in display_columns:
            display_columns.remove("last_edited")
        if "costs" in df.columns and "costs" in display_columns:
            pass
        column_mapping = {
            "order_id": "Mã đơn hàng",
            "error_code": "Thông báo lỗi",
        }
        df_display = df[[key for key in column_mapping if key in df.columns]]
        df_display.columns = [column_mapping[col] for col in df_display.columns]
        stream = io.BytesIO()
        df_display.to_excel(stream, index=False, engine='openpyxl')
        return rx.download(
            data=stream.getvalue(),
            filename="secondary_details_export.xlsx",
        )

    # Orders table methods
    def set_orders_search_customer(self, value: str):
        """Update the orders search customer filter."""
        self.orders_search_customer = value
        self.orders_current_page = 1

    def toggle_orders_sort(self, column_name: str):
        """Toggle sorting for a column in orders table."""
        if self.orders_sort_column == column_name:
            self.orders_sort_ascending = not self.orders_sort_ascending
        else:
            self.orders_sort_column = column_name
            self.orders_sort_ascending = True

    def orders_go_to_page(self, page_number: int):
        """Navigate to a specific page in orders table."""
        if 1 <= page_number <= self.orders_total_pages:
            self.orders_current_page = page_number

    def orders_next_page(self):
        """Go to the next page in orders table."""
        if self.orders_current_page < self.orders_total_pages:
            self.orders_current_page += 1

    def orders_previous_page(self):
        """Go to the previous page in orders table."""
        if self.orders_current_page > 1:
            self.orders_current_page -= 1

    def toggle_orders_row_selection(self, row_id: int):
        """Toggle selection state for a single row using its ID in orders table."""
        if row_id in self.orders_selected_rows:
            self.orders_selected_rows.remove(row_id)
        else:
            self.orders_selected_rows.add(row_id)

    def toggle_orders_select_all_on_page(self):
        """Select or deselect all rows on the current page in orders table."""
        page_ids = self.orders_page_item_ids
        if self.orders_all_rows_on_page_selected:
            self.orders_selected_rows -= page_ids
        else:
            self.orders_selected_rows.update(page_ids)

    def toggle_orders_type_filter(self):
        is_opening = not self.show_orders_type_filter
        self.show_orders_type_filter = is_opening
        self.show_orders_product_filter = False
        self.show_orders_revenue_filter = False
        self.show_orders_date_filter = False
        if is_opening:
            self.orders_temp_selected_types = (
                self.orders_selected_types.copy()
            )

    def toggle_orders_product_filter(self):
        is_opening = not self.show_orders_product_filter
        self.show_orders_product_filter = is_opening
        self.show_orders_type_filter = False
        self.show_orders_revenue_filter = False
        self.show_orders_date_filter = False
        if is_opening:
            self.orders_temp_selected_products = (
                self.orders_selected_products.copy()
            )

    def toggle_orders_revenue_filter(self):
        is_opening = not self.show_orders_revenue_filter
        self.show_orders_revenue_filter = is_opening
        self.show_orders_type_filter = False
        self.show_orders_product_filter = False
        self.show_orders_date_filter = False
        if is_opening:
            self.orders_temp_min_revenue_str = (
                str(self.orders_min_revenue)
                if self.orders_min_revenue is not None
                else ""
            )
            self.orders_temp_max_revenue_str = (
                str(self.orders_max_revenue)
                if self.orders_max_revenue is not None
                else ""
            )

    def toggle_orders_date_filter(self):
        is_opening = not self.show_orders_date_filter
        self.show_orders_date_filter = is_opening
        self.show_orders_type_filter = False
        self.show_orders_product_filter = False
        self.show_orders_revenue_filter = False
        if is_opening:
            self.orders_temp_start_date = (
                self.orders_start_date if self.orders_start_date is not None else ""
            )
            self.orders_temp_end_date = (
                self.orders_end_date if self.orders_end_date is not None else ""
            )

    def toggle_orders_temp_type(self, source_type: str):
        if source_type in self.orders_temp_selected_types:
            self.orders_temp_selected_types.remove(source_type)
        else:
            self.orders_temp_selected_types.add(source_type)

    def toggle_orders_temp_product(self, product: str):
        if product in self.orders_temp_selected_products:
            self.orders_temp_selected_products.remove(product)
        else:
            self.orders_temp_selected_products.add(product)

    def set_orders_temp_min_revenue(self, value: str):
        self.orders_temp_min_revenue_str = value

    def set_orders_temp_max_revenue(self, value: str):
        self.orders_temp_max_revenue_str = value

    def set_orders_temp_start_date(self, value: str):
        self.orders_temp_start_date = value

    def set_orders_temp_end_date(self, value: str):
        self.orders_temp_end_date = value

    def apply_orders_type_filter(self):
        self.orders_selected_types = (
            self.orders_temp_selected_types.copy()
        )
        self.show_orders_type_filter = False
        self.orders_current_page = 1

    def apply_orders_product_filter(self):
        self.orders_selected_products = (
            self.orders_temp_selected_products.copy()
        )
        self.show_orders_product_filter = False
        self.orders_current_page = 1

    def apply_orders_revenue_filter(self):
        new_min_revenue = None
        new_max_revenue = None
        try:
            if self.orders_temp_min_revenue_str:
                new_min_revenue = float(self.orders_temp_min_revenue_str)
        except ValueError:
            pass
        try:
            if self.orders_temp_max_revenue_str:
                new_max_revenue = float(self.orders_temp_max_revenue_str)
        except ValueError:
            pass
        self.orders_min_revenue = new_min_revenue
        self.orders_max_revenue = new_max_revenue
        self.show_orders_revenue_filter = False
        self.orders_current_page = 1

    def reset_orders_type_filter(self):
        self.orders_temp_selected_types = set()
        self.orders_selected_types = set()
        self.show_orders_type_filter = False
        self.orders_current_page = 1

    def reset_orders_product_filter(self):
        self.orders_temp_selected_products = set()
        self.orders_selected_products = set()
        self.show_orders_product_filter = False
        self.orders_current_page = 1

    def reset_orders_revenue_filter(self):
        self.orders_temp_min_revenue_str = ""
        self.orders_temp_max_revenue_str = ""
        self.orders_min_revenue = None
        self.orders_max_revenue = None
        self.show_orders_revenue_filter = False
        self.orders_current_page = 1

    def apply_orders_date_filter(self):
        self.orders_start_date = (
            self.orders_temp_start_date if self.orders_temp_start_date else None
        )
        self.orders_end_date = (
            self.orders_temp_end_date if self.orders_temp_end_date else None
        )
        self.show_orders_date_filter = False
        self.orders_current_page = 1

    def reset_orders_date_filter(self):
        self.orders_temp_start_date = ""
        self.orders_temp_end_date = ""
        self.orders_start_date = None
        self.orders_end_date = None
        self.show_orders_date_filter = False
        self.orders_current_page = 1

    def reset_all_orders_filters(self):
        """Reset all orders filters and search."""
        self.orders_search_customer = ""
        self.orders_selected_types = set()
        self.orders_selected_products = set()
        self.orders_min_revenue = None
        self.orders_max_revenue = None
        self.orders_start_date = None
        self.orders_end_date = None
        self.orders_temp_selected_types = set()
        self.orders_temp_selected_products = set()
        self.orders_temp_min_revenue_str = ""
        self.orders_temp_max_revenue_str = ""
        self.orders_temp_start_date = ""
        self.orders_temp_end_date = ""
        self.show_orders_type_filter = False
        self.show_orders_product_filter = False
        self.show_orders_revenue_filter = False
        self.show_orders_date_filter = False
        self.orders_current_page = 1
        self.orders_selected_rows = set()
        self.orders_sort_column = None
        self.orders_sort_ascending = True

    def refresh_orders_data(self):
        """Refresh orders data - reload from database."""
        self.load_orders_data()
        self._generate_fake_data()  # Regenerate metrics with new revenue data
        self.orders_selected_rows = set()
        self.orders_current_page = 1

    def toggle_orders_export_dropdown(self):
        """Toggle the export dropdown for orders table."""
        # Close other export dropdowns first
        self.show_export_dropdown = False
        self.show_secondary_export_dropdown = False
        # Toggle this dropdown
        self.show_orders_export_dropdown = not self.show_orders_export_dropdown

    @rx.event
    def download_orders_csv(self):
        """Download the orders data as CSV - selected rows if any are selected, otherwise all filtered data."""
        # If rows are selected, export only selected rows, otherwise export all filtered data
        if self.orders_selected_rows:
            data_to_export = [
                item for item in self.orders_filtered_and_sorted_data
                if item["id"] in self.orders_selected_rows
            ]
        else:
            data_to_export = self.orders_filtered_and_sorted_data

        df = pd.DataFrame(data_to_export)
        display_columns = [
            col.lower()
            .replace(" ", "_")
            .replace("ã", "a")
            .replace("ô", "o")
            .replace("ư", "u")
            for col in self.orders_column_names
            if col != "Edit"
        ]
        column_mapping = {
            "order_date": "Ngày Ct",
            "document_type": "Mã Ct",
            "document_number": "Số Ct",
            "department_code": "Mã bộ phận",
            "order_id": "Mã đơn hàng",
            "customer_name": "Tên khách hàng",
            "phone_number": "Số điện thoại",
            "district": "Quận huyện",
            "ward": "Phường xã",
            "address": "Địa chỉ",
            "product_code": "Mã hàng",
            "product_name": "Tên hàng",
            "imei": "Imei",
            "quantity": "Số lượng",
            "revenue": "Doanh thu",
            "error_code": "Ghi chú",
        }
        df_display = df[[key for key in column_mapping if key in df.columns]]
        df_display.columns = [column_mapping[col] for col in df_display.columns]
        stream = io.StringIO()
        df_display.to_csv(stream, index=False)
        return rx.download(
            data=stream.getvalue(),
            filename="orders_export.csv",
        )

    @rx.event
    def download_orders_xlsx(self):
        """Download the orders data as XLSX - selected rows if any are selected, otherwise all filtered data."""
        # If rows are selected, export only selected rows, otherwise export all filtered data
        if self.orders_selected_rows:
            data_to_export = [
                item for item in self.orders_filtered_and_sorted_data
                if item["id"] in self.orders_selected_rows
            ]
        else:
            data_to_export = self.orders_filtered_and_sorted_data

        df = pd.DataFrame(data_to_export)
        display_columns = [
            col.lower()
            .replace(" ", "_")
            .replace("ã", "a")
            .replace("ô", "o")
            .replace("ư", "u")
            for col in self.orders_column_names
            if col != "Edit"
        ]
        column_mapping = {
            "order_date": "Ngày Ct",
            "document_type": "Mã Ct",
            "document_number": "Số Ct",
            "department_code": "Mã bộ phận",
            "order_id": "Mã đơn hàng",
            "customer_name": "Tên khách hàng",
            "phone_number": "Số điện thoại",
            "district": "Quận huyện",
            "ward": "Phường xã",
            "address": "Địa chỉ",
            "product_code": "Mã hàng",
            "product_name": "Tên hàng",
            "imei": "Imei",
            "quantity": "Số lượng",
            "revenue": "Doanh thu",
            "error_code": "Ghi chú",
        }
        df_display = df[[key for key in column_mapping if key in df.columns]]
        df_display.columns = [column_mapping[col] for col in df_display.columns]
        stream = io.BytesIO()
        df_display.to_excel(stream, index=False, engine='openpyxl')
        return rx.download(
            data=stream.getvalue(),
            filename="orders_export.xlsx",
        )

    # Product codes table methods
    def product_codes_go_to_page(self, page_number: int):
        """Navigate to a specific page in product codes table."""
        if 1 <= page_number <= self.product_codes_total_pages:
            self.product_codes_current_page = page_number

    def product_codes_next_page(self):
        """Go to the next page in product codes table."""
        if self.product_codes_current_page < self.product_codes_total_pages:
            self.product_codes_current_page += 1

    def product_codes_previous_page(self):
        """Go to the previous page in product codes table."""
        if self.product_codes_current_page > 1:
            self.product_codes_current_page -= 1


TOOLTIP_PROPS = {
    "separator": ": ",
    "cursor": False,
    "is_animation_active": False,
    "label_style": {"fontWeight": "500"},
    "item_style": {
        "color": "currentColor",
        "display": "flex",
        "paddingBottom": "0px",
        "justifyContent": "space-between",
        "textTransform": "capitalize",
    },
    "content_style": {
        "borderRadius": "5px",
        "boxShadow": "0px 2px 6px 0px rgba(0, 0, 0, 0.1)",
        "fontSize": "0.75rem",
        "lineHeight": "1rem",
        "fontWeight": "500",
        "minWidth": "8rem",
        "width": "auto",
        "padding": "0.375rem 0.625rem",
        "backgroundColor": "white",
        "border": "1px solid #e2e8f0",
    },
}
