import reflex as rx
from data_dashboard.states.dashboard_state import DashboardState


def summary_bar_segment(percentage: rx.Var[float], color: str) -> rx.Component:
    """Creates a segment of the summary bar."""
    return rx.el.div(
        class_name=f"{color} h-3",
        style={"width": percentage.to_string() + "%"},
    )


def summary_list_item(
    label: str,
    value: rx.Var[int],
    percentage: rx.Var[float],
    color: str,
) -> rx.Component:
    """Displays a single item in the summary list."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(class_name=f"{color} w-3 h-3 rounded-full mr-3"),
            rx.el.span(
                label,
                class_name="text-sm text-gray-700",
            ),
            class_name="flex items-center",
        ),
        rx.el.div(
            rx.el.span(
                value.to_string(),
                class_name="text-sm font-medium text-gray-900 mr-2",
            ),
            rx.el.span(
                "(" + percentage.to_string() + "%)",
                class_name="text-xs text-gray-500",
            ),
            class_name="flex items-center",
        ),
        class_name="flex items-center justify-between py-2",
    )


def orders_summary_section() -> rx.Component:
    """Displays the Orders Summary with online/offline percentages."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Tóm tắt đơn hàng",
                class_name="text-lg font-semibold text-gray-900",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    "Trạng thái đơn hàng",
                    class_name="text-sm font-medium text-gray-500 mb-2",
                ),
                rx.el.span(
                    DashboardState.orders_status_summary["total_orders"].to_string() + " đơn",
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="flex items-center justify-between mb-3",
            ),
            rx.el.div(
                summary_bar_segment(
                    DashboardState.orders_status_summary["online_percent"],
                    "bg-green-500"
                ),
                summary_bar_segment(
                    DashboardState.orders_status_summary["offline_percent"],
                    "bg-red-500"
                ),
                class_name="flex w-full h-3 bg-gray-200 rounded-full overflow-hidden mb-4",
            ),
            rx.el.div(
                summary_list_item(
                    "Online",
                    DashboardState.orders_status_summary["online_orders"],
                    DashboardState.orders_status_summary["online_percent"],
                    "bg-green-500",
                ),
                summary_list_item(
                    "Offline",
                    DashboardState.orders_status_summary["offline_orders"],
                    DashboardState.orders_status_summary["offline_percent"],
                    "bg-red-500",
                ),
                class_name="space-y-1",
            ),
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-lg shadow-sm",
    )