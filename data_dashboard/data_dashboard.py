import reflex as rx

from data_dashboard.components.details_table import details_table
from data_dashboard.components.filter_dropdown import (
    costs_filter_dropdown,
    date_filter_dropdown,
    export_dropdown,
    filter_button,
    orders_product_filter_dropdown,
    orders_type_filter_dropdown,
    orders_revenue_filter_dropdown,
    region_filter_dropdown,
    status_filter_dropdown,
)
from data_dashboard.components.header import header_bar
from data_dashboard.components.key_metrics import key_metrics_section
from data_dashboard.components.orders_table import orders_table
from data_dashboard.components.orders_summary import orders_summary_section
from data_dashboard.components.product_codes_table import product_codes_table
from data_dashboard.components.sidebar import sidebar
from data_dashboard.components.visitors_chart import visitors_chart_section
from data_dashboard.states.dashboard_state import DashboardState


def overview_section() -> rx.Component:
    """The Overview section containing company dashboard components."""
    return rx.el.div(
        key_metrics_section(),
        visitors_chart_section(),
        class_name="space-y-6",
    )


def orders_table_header() -> rx.Component:
    """Enhanced header with search, export, view functionality for orders table."""
    return rx.el.div(
        rx.el.h1(
            "Orders Data",
            class_name="text-2xl font-semibold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    filter_button(
                        "Type",
                        on_click=DashboardState.toggle_orders_type_filter,
                        is_active=DashboardState.show_orders_type_filter,
                        has_filter=DashboardState.orders_selected_types.length()
                        > 0,
                    ),
                    orders_type_filter_dropdown(),
                    class_name="relative",
                ),
                rx.el.div(
                    filter_button(
                        "Product",
                        on_click=DashboardState.toggle_orders_product_filter,
                        is_active=DashboardState.show_orders_product_filter,
                        has_filter=DashboardState.orders_selected_products.length()
                        > 0,
                    ),
                    orders_product_filter_dropdown(),
                    class_name="relative",
                ),
                rx.el.div(
                    filter_button(
                        "Revenue",
                        on_click=DashboardState.toggle_orders_revenue_filter,
                        is_active=DashboardState.show_orders_revenue_filter,
                        has_filter=DashboardState.orders_min_revenue
                        | DashboardState.orders_max_revenue,
                    ),
                    orders_revenue_filter_dropdown(),
                    class_name="relative",
                ),
                rx.el.div(
                    filter_button(
                        "Date",
                        on_click=DashboardState.toggle_orders_date_filter,
                        is_active=DashboardState.show_orders_date_filter,
                        has_filter=DashboardState.orders_start_date
                        | DashboardState.orders_end_date,
                    ),
                    date_filter_dropdown(is_orders=True),
                    class_name="relative",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            tag="search",
                            size=18,
                            class_name="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="Search by customer...",
                            on_change=DashboardState.set_orders_search_customer.debounce(
                                300
                            ),
                            class_name="pl-10 pr-4 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                            default_value=DashboardState.orders_search_customer,
                        ),
                        class_name="relative flex items-center -ml-2 sm:ml-0",
                    ),
                    rx.el.button(
                        "Reset All",
                        on_click=DashboardState.reset_all_orders_filters,
                        class_name="px-3 py-1.5 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50",
                        disabled=(DashboardState.orders_search_customer == "")
                        & (
                            DashboardState.orders_selected_types.length()
                            == 0
                        )
                        & (
                            DashboardState.orders_selected_products.length()
                            == 0
                        )
                        & (DashboardState.orders_min_revenue is None)
                        & (DashboardState.orders_max_revenue is None)
                        & (DashboardState.orders_start_date is None)
                        & (DashboardState.orders_end_date is None),
                    ),
                    rx.el.button(
                        rx.icon(
                            tag="refresh_cw",
                            class_name="w-4 h-4 mr-2",
                        ),
                        "Refresh all",
                        on_click=DashboardState.refresh_orders_data,
                        class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition",
                    ),
                    class_name="flex flex-row items-center justify-start gap-x-2",
                ),
                class_name="flex items-center space-x-2 flex-wrap gap-y-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon(
                            tag="upload",
                            size=16,
                            class_name="mr-1.5",
                        ),
                        "Export",
                        rx.icon(
                            tag="chevron_down",
                            size=14,
                            class_name="ml-1",
                        ),
                        on_click=DashboardState.toggle_orders_export_dropdown,
                        disabled=DashboardState.orders_filtered_and_sorted_data.length()
                        <= 0,
                        class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    export_dropdown(
                        show_dropdown=DashboardState.show_orders_export_dropdown,
                        csv_action=DashboardState.download_orders_csv,
                        xlsx_action=DashboardState.download_orders_xlsx,
                        is_disabled=DashboardState.orders_filtered_and_sorted_data.length()
                        <= 0,
                    ),
                    class_name="relative",
                ),
                rx.el.button(
                    rx.icon(
                        tag="eye",
                        size=16,
                        class_name="mr-1.5",
                    ),
                    "View",
                    class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition",
                ),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex items-center justify-between flex-wrap gap-y-3",
        ),
    )


def data_table_header() -> rx.Component:
    """Enhanced header with search, export, view functionality."""
    return rx.el.div(
        rx.el.h1(
            "Details",
            class_name="text-2xl font-semibold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    filter_button(
                        "Status",
                        on_click=DashboardState.toggle_status_filter,
                        is_active=DashboardState.show_status_filter,
                        has_filter=DashboardState.selected_statuses.length()
                        > 0,
                    ),
                    status_filter_dropdown(),
                    class_name="relative",
                ),
                rx.el.div(
                    filter_button(
                        "Region",
                        on_click=DashboardState.toggle_region_filter,
                        is_active=DashboardState.show_region_filter,
                        has_filter=DashboardState.selected_regions.length() > 0,
                    ),
                    region_filter_dropdown(),
                    class_name="relative",
                ),
                rx.el.div(
                    filter_button(
                        "Costs",
                        on_click=DashboardState.toggle_costs_filter,
                        is_active=DashboardState.show_costs_filter,
                        has_filter=DashboardState.min_cost
                        | DashboardState.max_cost,
                    ),
                    costs_filter_dropdown(),
                    class_name="relative",
                ),
                rx.el.div(
                    filter_button(
                        "Date",
                        on_click=DashboardState.toggle_date_filter,
                        is_active=DashboardState.show_date_filter,
                        has_filter=DashboardState.start_date
                        | DashboardState.end_date,
                    ),
                    date_filter_dropdown(is_orders=False),
                    class_name="relative",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            tag="search",
                            size=18,
                            class_name="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="Search by owner...",
                            on_change=DashboardState.set_search_owner.debounce(
                                300
                            ),
                            class_name="pl-10 pr-4 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                            default_value=DashboardState.search_owner,
                        ),
                        class_name="relative flex items-center -ml-2 sm:ml-0",
                    ),
                    rx.el.button(
                        "Reset All",
                        on_click=DashboardState.reset_all_filters,
                        class_name="px-3 py-1.5 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50",
                        disabled=(DashboardState.search_owner == "")
                        & (DashboardState.selected_statuses.length() == 0)
                        & (DashboardState.selected_regions.length() == 0)
                        & (DashboardState.min_cost is None)
                        & (DashboardState.max_cost is None)
                        & (DashboardState.start_date is None)
                        & (DashboardState.end_date is None),
                    ),
                    rx.el.button(
                        rx.icon(
                            tag="refresh_cw",
                            class_name="w-4 h-4 mr-2",
                        ),
                        "Refresh all",
                        on_click=DashboardState.refresh_all_data,
                        class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition",
                    ),
                    class_name="flex flex-row items-center justify-start gap-x-2",
                ),
                class_name="flex items-center space-x-2 flex-wrap gap-y-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon(
                            tag="upload",
                            size=16,
                            class_name="mr-1.5",
                        ),
                        "Export",
                        rx.icon(
                            tag="chevron_down",
                            size=14,
                            class_name="ml-1",
                        ),
                        on_click=DashboardState.toggle_export_dropdown,
                        disabled=DashboardState.filtered_and_sorted_data.length()
                        <= 0,
                        class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    export_dropdown(
                        show_dropdown=DashboardState.show_export_dropdown,
                        csv_action=DashboardState.download_csv,
                        xlsx_action=DashboardState.download_xlsx,
                        is_disabled=DashboardState.filtered_and_sorted_data.length()
                        <= 0,
                    ),
                    class_name="relative",
                ),
                rx.el.button(
                    rx.icon(
                        tag="eye",
                        size=16,
                        class_name="mr-1.5",
                    ),
                    "View",
                    class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition",
                ),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex items-center justify-between flex-wrap gap-y-3",
        ),
    )


def secondary_data_table_header() -> rx.Component:
    """Enhanced header with search, export, view functionality for second table."""
    return rx.el.div(
        rx.el.h1(
            "Order Error Data",
            class_name="text-2xl font-semibold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            tag="search",
                            size=18,
                            class_name="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="Search by order ID...",
                            on_change=DashboardState.set_secondary_search_owner.debounce(
                                300
                            ),
                            class_name="pl-10 pr-4 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                            default_value=DashboardState.secondary_search_owner,
                        ),
                        class_name="relative flex items-center -ml-2 sm:ml-0",
                    ),
                    rx.el.button(
                        "Reset All",
                        on_click=DashboardState.reset_all_secondary_filters,
                        class_name="px-3 py-1.5 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50",
                        disabled=(DashboardState.secondary_search_owner == ""),
                    ),
                    rx.el.button(
                        rx.icon(
                            tag="refresh_cw",
                            class_name="w-4 h-4 mr-2",
                        ),
                        "Refresh all",
                        on_click=DashboardState.refresh_secondary_data,
                        class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition",
                    ),
                    class_name="flex flex-row items-center justify-start gap-x-2",
                ),
                class_name="flex items-center space-x-2 flex-wrap gap-y-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon(
                            tag="upload",
                            size=16,
                            class_name="mr-1.5",
                        ),
                        "Export",
                        rx.icon(
                            tag="chevron_down",
                            size=14,
                            class_name="ml-1",
                        ),
                        on_click=DashboardState.toggle_secondary_export_dropdown,
                        disabled=DashboardState.secondary_filtered_and_sorted_data.length()
                        <= 0,
                        class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    export_dropdown(
                        show_dropdown=DashboardState.show_secondary_export_dropdown,
                        csv_action=DashboardState.download_secondary_csv,
                        xlsx_action=DashboardState.download_secondary_xlsx,
                        is_disabled=DashboardState.secondary_filtered_and_sorted_data.length()
                        <= 0,
                    ),
                    class_name="relative",
                ),
                rx.el.button(
                    rx.icon(
                        tag="eye",
                        size=16,
                        class_name="mr-1.5",
                    ),
                    "View",
                    class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition",
                ),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex items-center justify-between flex-wrap gap-y-3",
        ),
    )


def data_section() -> rx.Component:
    """The Data section containing table dashboard components."""
    return rx.el.div(
        # Main tables section (Orders and Error data)
        rx.el.div(
            orders_table_header(),
            rx.el.div(
                orders_table(),
                class_name="mt-6",
            ),
            rx.el.div(
                secondary_data_table_header(),
                rx.el.div(
                    details_table(is_secondary=True),
                    class_name="mt-6",
                ),
                class_name="mt-8",
            ),
            class_name="space-y-6 mb-8",
        ),
        # New layout section (similar to account_section and summary_section)
        rx.el.div(
            rx.el.div(
                product_codes_table(),
                class_name="flex-grow pr-0 lg:pr-8 mb-8 lg:mb-0",
            ),
            rx.el.div(
                orders_summary_section(),
                class_name="w-full lg:w-80 flex-shrink-0",
            ),
            class_name="flex flex-col lg:flex-row",
        ),
        class_name="space-y-6",
    )


def index() -> rx.Component:
    """The main dashboard page with sidebar navigation."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            header_bar(),
            rx.el.div(
                rx.cond(
                    DashboardState.selected_section == "overview",
                    overview_section(),
                    data_section(),
                ),
                class_name="p-6",
            ),
            class_name="w-full h-[100vh] overflow-y-auto",
        ),
        class_name="flex flex-row bg-gray-50 h-[100vh] w-full overflow-hidden",
        on_mount=DashboardState.load_initial_data,
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=["https://cdn.tailwindcss.com"],
    style={
        rx.el.label: {"font_family": "JetBrains Mono,ui-monospace,monospace"},
        rx.el.span: {"font_family": "JetBrains Mono,ui-monospace,monospace"},
        rx.el.h1: {"font_family": "JetBrains Mono,ui-monospace,monospace"},
        rx.el.h2: {"font_family": "JetBrains Mono,ui-monospace,monospace"},
    },
)
app.add_page(index, route="/")
