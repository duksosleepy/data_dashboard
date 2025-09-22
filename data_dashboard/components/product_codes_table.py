import reflex as rx
from data_dashboard.states.dashboard_state import DashboardState


def product_codes_table() -> rx.Component:
    """Table showing non-existing product codes with compact design."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Mã hàng không tồn tại",
                class_name="text-lg font-semibold text-gray-900 mb-3",
            ),
            rx.el.div(
                f"Tổng: {DashboardState.product_codes_total_rows}",
                class_name="text-sm text-gray-600 mb-2",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Mã hàng",
                                class_name="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 border-b border-gray-200",
                            ),
                        ),
                        class_name="sticky top-0 z-10 bg-gray-50",
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            DashboardState.product_codes_paginated_data,
                            lambda item: rx.el.tr(
                                rx.el.td(
                                    item["product_code"],
                                    class_name="px-3 py-2 text-sm text-gray-900 border-b border-gray-100",
                                ),
                                class_name="hover:bg-gray-50 bg-white",
                            ),
                        ),
                        class_name="divide-y divide-gray-100",
                    ),
                    class_name="min-w-full",
                ),
                class_name="overflow-auto border border-gray-200 rounded-lg",
                style={"max-height": "400px"},
            ),
            # Pagination controls (compact)
            rx.cond(
                DashboardState.product_codes_total_pages > 1,
                rx.el.div(
                    rx.el.div(
                        rx.el.button(
                            "‹",
                            on_click=DashboardState.product_codes_previous_page,
                            disabled=DashboardState.product_codes_current_page == 1,
                            class_name="px-2 py-1 text-sm border border-gray-300 rounded-l bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
                        ),
                        rx.el.span(
                            f"{DashboardState.product_codes_current_page}/{DashboardState.product_codes_total_pages}",
                            class_name="px-3 py-1 text-sm border-t border-b border-gray-300 bg-white",
                        ),
                        rx.el.button(
                            "›",
                            on_click=DashboardState.product_codes_next_page,
                            disabled=DashboardState.product_codes_current_page == DashboardState.product_codes_total_pages,
                            class_name="px-2 py-1 text-sm border border-gray-300 rounded-r bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="flex justify-center",
                ),
            ),
            class_name="space-y-0",
        ),
        class_name="p-4 bg-white border border-gray-200 rounded-lg shadow-sm",
    )