import reflex as rx

from data_dashboard.states.dashboard_state import (
    DashboardState,
)


def status_badge(status: rx.Var[str]) -> rx.Component:
    """Creates a colored status badge."""
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "Live",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
            ),
            (
                "Inactive",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800",
            ),
            (
                "Archived",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800",
            ),
            "px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800",
        ),
    )


def table_header_cell(name: str, is_sortable: bool = True, is_secondary: bool = False) -> rx.Component:
    """Creates a table header cell with optional sorting."""
    # Choose the appropriate state variables and functions
    if is_secondary:
        sort_column = DashboardState.secondary_sort_column
        sort_ascending = DashboardState.secondary_sort_ascending
        toggle_sort = DashboardState.toggle_secondary_sort
    else:
        sort_column = DashboardState.sort_column
        sort_ascending = DashboardState.sort_ascending
        toggle_sort = DashboardState.toggle_sort

    return rx.el.th(
        rx.el.div(
            name,
            rx.cond(
                is_sortable,
                rx.el.span(
                    rx.icon(
                        tag=rx.cond(
                            (sort_column == name) & sort_ascending,
                            "arrow_upward",
                            "arrow_downward",
                        ),
                        size=14,
                        class_name=rx.cond(
                            sort_column == name,
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
                toggle_sort(name),
                rx.noop(),
            ),
        ),
        scope="col",
        class_name="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 border-b border-gray-200 select-none",
    )


def details_table(is_secondary: bool = False) -> rx.Component:
    """The main table component displaying details."""
    # Choose the appropriate state variables based on whether this is secondary table
    if is_secondary:
        paginated_data = DashboardState.secondary_paginated_data
        selected_rows = DashboardState.secondary_selected_rows
        all_rows_selected = DashboardState.secondary_all_rows_on_page_selected
        total_rows = DashboardState.secondary_total_rows
        current_rows_display = DashboardState.secondary_current_rows_display
        current_page = DashboardState.secondary_current_page
        total_pages = DashboardState.secondary_total_pages
        sort_column = DashboardState.secondary_sort_column
        sort_ascending = DashboardState.secondary_sort_ascending
        toggle_select_all = DashboardState.toggle_secondary_select_all_on_page
        toggle_row_selection = DashboardState.toggle_secondary_row_selection
        toggle_sort = DashboardState.toggle_secondary_sort
        next_page = DashboardState.secondary_next_page
        previous_page = DashboardState.secondary_previous_page
    else:
        paginated_data = DashboardState.paginated_data
        selected_rows = DashboardState.selected_rows
        all_rows_selected = DashboardState.all_rows_on_page_selected
        total_rows = DashboardState.total_rows
        current_rows_display = DashboardState.current_rows_display
        current_page = DashboardState.current_page
        total_pages = DashboardState.total_pages
        sort_column = DashboardState.sort_column
        sort_ascending = DashboardState.sort_ascending
        toggle_select_all = DashboardState.toggle_select_all_on_page
        toggle_row_selection = DashboardState.toggle_row_selection
        toggle_sort = DashboardState.toggle_sort
        next_page = DashboardState.next_page
        previous_page = DashboardState.previous_page

    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            rx.el.input(
                                type="checkbox",
                                class_name="h-4 w-4 border-gray-300 rounded text-blue-600 focus:ring-blue-500 cursor-pointer",
                                on_change=toggle_select_all,
                                checked=all_rows_selected & (paginated_data.length() > 0),
                                disabled=paginated_data.length() <= 0,
                            ),
                            scope="col",
                            class_name="px-3 py-3 whitespace-nowrap w-12 bg-gray-50 border-b border-gray-200",
                        ),
                        rx.foreach(
                            rx.cond(
                                is_secondary,
                                DashboardState.column_names,  # Vietnamese headers for secondary table
                                ["Owner", "Status", "Region", "Stability", "Costs", "Last edited", "Edit"]  # Original headers for primary table
                            ),
                            lambda name: table_header_cell(
                                name,
                                is_sortable=name != "Edit",
                                is_secondary=is_secondary,
                            ),
                        ),
                    ),
                    class_name="sticky top-0 z-10 bg-gray-50",
                ),
                rx.el.tbody(
                    rx.foreach(
                        paginated_data,
                        lambda row: rx.el.tr(
                            rx.el.td(
                                rx.el.input(
                                    type="checkbox",
                                    class_name="h-4 w-4 border-gray-300 rounded text-blue-600 focus:ring-blue-500 cursor-pointer",
                                    on_change=lambda: toggle_row_selection(row["id"]),
                                    checked=selected_rows.contains(row["id"]),
                                ),
                                class_name="px-3 py-2 whitespace-nowrap w-12 border-b border-gray-100",
                            ),
                            rx.cond(
                                is_secondary,
                                # Secondary table: order_id and error_code only
                                rx.fragment(
                                    rx.el.td(
                                        row["order_id"],
                                        class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                                    ),
                                    rx.el.td(
                                        row["error_code"],
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
                                ),
                                # Primary table: original columns
                                rx.fragment(
                                    rx.el.td(
                                        row["owner"],
                                        class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                                    ),
                                    rx.el.td(
                                        status_badge(row["status"]),
                                        class_name="px-3 py-2 whitespace-nowrap text-sm border-b border-gray-100",
                                    ),
                                    rx.el.td(
                                        row["region"],
                                        class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                                    ),
                                    rx.el.td(
                                        row["stability"].to_string(),
                                        class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                                    ),
                                    rx.el.td(
                                        "$" + row["costs"].to_string(),
                                        class_name="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100",
                                    ),
                                    rx.el.td(
                                        row["last_edited"],
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
                                ),
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
                selected_rows.length().to_string()
                + " of "
                + total_rows.to_string()
                + " row(s) selected.",
                class_name="text-sm text-gray-500",
            ),
            rx.el.div(
                rx.el.span(
                    "Showing "
                    + current_rows_display
                    + " of "
                    + total_rows.to_string(),
                    class_name="text-sm text-gray-500 mr-4",
                ),
                rx.el.button(
                    rx.icon(tag="chevron_left", size=18),
                    on_click=previous_page,
                    disabled=current_page <= 1,
                    class_name="p-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50",
                ),
                rx.el.button(
                    rx.icon(tag="chevron_right", size=18),
                    on_click=next_page,
                    disabled=current_page >= total_pages,
                    class_name="p-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 ml-2",
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-between px-4 py-2 border-t border-gray-200 bg-white rounded-b-lg",
        ),
        class_name="shadow-sm",
    )
