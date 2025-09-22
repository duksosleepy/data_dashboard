import reflex as rx

from data_dashboard.states.dashboard_state import DashboardState


def orders_table_header_cell(name: str, is_sortable: bool = True) -> rx.Component:
    """Creates a table header cell with optional sorting for orders table."""
    return rx.el.th(
        rx.el.div(
            name,
            rx.cond(
                is_sortable,
                rx.el.span(
                    rx.icon(
                        tag=rx.cond(
                            (DashboardState.orders_sort_column == name) & DashboardState.orders_sort_ascending,
                            "arrow_upward",
                            "arrow_downward",
                        ),
                        size=14,
                        class_name=rx.cond(
                            DashboardState.orders_sort_column == name,
                            "text-gray-800",
                            "text-gray-400 hover:text-gray-600",
                        ),
                    ),
                    class_name="ml-1 opacity-70 hover:opacity-100",
                ),
                rx.el.span(),
            ),
            class_name="flex items-center justify-between group cursor-pointer",
            on_click=rx.cond(
                is_sortable,
                DashboardState.toggle_orders_sort(name),
                rx.noop(),
            ),
        ),
        scope="col",
        class_name="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 border-b border-gray-200 select-none",
    )


def orders_table() -> rx.Component:
    """The orders table component displaying DuckDB data."""
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            rx.el.input(
                                type="checkbox",
                                class_name="h-4 w-4 border-gray-300 rounded text-blue-600 focus:ring-blue-500 cursor-pointer",
                                on_change=DashboardState.toggle_orders_select_all_on_page,
                                checked=DashboardState.orders_all_rows_on_page_selected
                                & (DashboardState.orders_paginated_data.length() > 0),
                                disabled=DashboardState.orders_paginated_data.length() <= 0,
                            ),
                            scope="col",
                            class_name="px-3 py-3 whitespace-nowrap w-12 bg-gray-50 border-b border-gray-200",
                        ),
                        rx.foreach(
                            DashboardState.orders_column_names,
                            lambda name: orders_table_header_cell(
                                name,
                                is_sortable=name != "Edit",
                            ),
                        ),
                    ),
                    class_name="sticky top-0 z-10 bg-gray-50",
                ),
                rx.el.tbody(
                    rx.foreach(
                        DashboardState.orders_paginated_data,
                        lambda row: rx.el.tr(
                            rx.el.td(
                                rx.el.input(
                                    type="checkbox",
                                    class_name="h-4 w-4 border-gray-300 rounded text-blue-600 focus:ring-blue-500 cursor-pointer",
                                    on_change=lambda: DashboardState.toggle_orders_row_selection(row["id"]),
                                    checked=DashboardState.orders_selected_rows.contains(row["id"]),
                                ),
                                class_name="px-3 py-2 whitespace-nowrap w-12 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["order_date"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["document_type"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["document_number"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["department_code"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["order_id"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["customer_name"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["phone_number"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["province"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["district"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["ward"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["address"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100 max-w-xs truncate",
                            ),
                            rx.el.td(
                                row["product_code"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["product_name"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100 max-w-xs truncate",
                            ),
                            rx.el.td(
                                row["imei"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["quantity"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["revenue"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["error_code"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                row["source_type"],
                                class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                            ),
                            rx.el.td(
                                rx.el.button(
                                    rx.icon(
                                        tag="send_horizontal",
                                        size=16,
                                    ),
                                    variant="ghost",
                                    class_name="text-gray-400 hover:text-gray-600",
                                ),
                                class_name="px-3 py-2 whitespace-nowrap text-right text-sm font-medium border-b border-gray-100",
                            ),
                            class_name="hover:bg-gray-50 bg-white",
                        ),
                    ),
                    class_name="divide-y divide-gray-100",
                ),
                class_name="min-w-full",
            ),
            class_name="overflow-auto border border-gray-200 rounded-lg",
        ),
        rx.el.div(
            rx.el.p(
                DashboardState.orders_selected_rows.length().to_string()
                + " of "
                + DashboardState.orders_total_rows.to_string()
                + " row(s) selected.",
                class_name="text-sm text-gray-500",
            ),
            rx.el.div(
                rx.el.span(
                    "Showing "
                    + DashboardState.orders_current_rows_display
                    + " of "
                    + DashboardState.orders_total_rows.to_string(),
                    class_name="text-sm text-gray-500 mr-4",
                ),
                rx.el.button(
                    rx.icon(tag="chevron_left", size=18),
                    on_click=DashboardState.orders_previous_page,
                    disabled=DashboardState.orders_current_page <= 1,
                    class_name="p-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50",
                ),
                rx.el.button(
                    rx.icon(tag="chevron_right", size=18),
                    on_click=DashboardState.orders_next_page,
                    disabled=DashboardState.orders_current_page >= DashboardState.orders_total_pages,
                    class_name="p-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 ml-2",
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-between px-4 py-2 border-t border-gray-200 bg-white rounded-b-lg",
        ),
        class_name="shadow-sm",
    )