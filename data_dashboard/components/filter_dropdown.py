from typing import Callable

import reflex as rx
from reflex.event import EventSpec

from data_dashboard.states.dashboard_state import DashboardState


def filter_checkbox_item(
    label: str,
    is_checked: rx.Var[bool],
    on_change: Callable[[str], None],
) -> rx.Component:
    """Component for a single checkbox item in a filter dropdown."""
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            checked=is_checked,
            on_change=lambda: on_change(label),
            class_name="mr-2 h-4 w-4 border-gray-300 rounded text-blue-600 focus:ring-blue-500 cursor-pointer",
        ),
        label,
        class_name="flex items-center text-sm text-gray-700 p-2 hover:bg-gray-50 cursor-pointer rounded",
    )


def status_filter_dropdown(is_secondary: bool = False) -> rx.Component:
    """Dropdown component for filtering by Status."""
    if is_secondary:
        temp_selected = DashboardState.secondary_temp_selected_statuses
        show_filter = DashboardState.show_secondary_status_filter
        toggle_temp = DashboardState.toggle_secondary_temp_status
        reset_filter = DashboardState.reset_secondary_status_filter
        apply_filter = DashboardState.apply_secondary_status_filter
    else:
        temp_selected = DashboardState.temp_selected_statuses
        show_filter = DashboardState.show_status_filter
        toggle_temp = DashboardState.toggle_temp_status
        reset_filter = DashboardState.reset_status_filter
        apply_filter = DashboardState.apply_status_filter

    return rx.el.div(
        rx.el.p(
            "Filter by Status",
            class_name="text-xs font-semibold text-gray-500 px-3 pt-2 pb-1",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.unique_statuses,
                lambda status: filter_checkbox_item(
                    label=status,
                    is_checked=temp_selected.contains(status),
                    on_change=toggle_temp,
                ),
            ),
            class_name="max-h-48 overflow-y-auto p-1",
        ),
        rx.el.div(
            rx.el.button(
                "Reset",
                on_click=reset_filter,
                class_name="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded",
            ),
            rx.el.button(
                "Apply",
                on_click=apply_filter,
                class_name="px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded",
            ),
            class_name="flex justify-end space-x-2 p-2 border-t border-gray-200",
        ),
        class_name="absolute top-full left-0 mt-1 w-56 border border-gray-300 rounded z-10 bg-white shadow-lg",
        hidden=~show_filter,
    )


def region_filter_dropdown(is_secondary: bool = False) -> rx.Component:
    """Dropdown component for filtering by Region."""
    if is_secondary:
        temp_selected = DashboardState.secondary_temp_selected_regions
        show_filter = DashboardState.show_secondary_region_filter
        toggle_temp = DashboardState.toggle_secondary_temp_region
        reset_filter = DashboardState.reset_secondary_region_filter
        apply_filter = DashboardState.apply_secondary_region_filter
    else:
        temp_selected = DashboardState.temp_selected_regions
        show_filter = DashboardState.show_region_filter
        toggle_temp = DashboardState.toggle_temp_region
        reset_filter = DashboardState.reset_region_filter
        apply_filter = DashboardState.apply_region_filter

    return rx.el.div(
        rx.el.p(
            "Filter by Region",
            class_name="text-xs font-semibold text-gray-500 px-3 pt-2 pb-1",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.unique_regions,
                lambda region: filter_checkbox_item(
                    label=region,
                    is_checked=temp_selected.contains(region),
                    on_change=toggle_temp,
                ),
            ),
            class_name="max-h-48 overflow-y-auto p-1",
        ),
        rx.el.div(
            rx.el.button(
                "Reset",
                on_click=reset_filter,
                class_name="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded",
            ),
            rx.el.button(
                "Apply",
                on_click=apply_filter,
                class_name="px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded",
            ),
            class_name="flex justify-end space-x-2 p-2 border-t border-gray-200",
        ),
        class_name="absolute top-full left-0 mt-1 w-56 border border-gray-300 rounded z-10 bg-white shadow-lg",
        hidden=~show_filter,
    )


def costs_filter_dropdown(is_secondary: bool = False) -> rx.Component:
    """Dropdown component for filtering by Costs."""
    if is_secondary:
        temp_min_cost_str = DashboardState.secondary_temp_min_cost_str
        temp_max_cost_str = DashboardState.secondary_temp_max_cost_str
        show_filter = DashboardState.show_secondary_costs_filter
        set_temp_min = DashboardState.set_secondary_temp_min_cost
        set_temp_max = DashboardState.set_secondary_temp_max_cost
        reset_filter = DashboardState.reset_secondary_costs_filter
        apply_filter = DashboardState.apply_secondary_costs_filter
    else:
        temp_min_cost_str = DashboardState.temp_min_cost_str
        temp_max_cost_str = DashboardState.temp_max_cost_str
        show_filter = DashboardState.show_costs_filter
        set_temp_min = DashboardState.set_temp_min_cost
        set_temp_max = DashboardState.set_temp_max_cost
        reset_filter = DashboardState.reset_costs_filter
        apply_filter = DashboardState.apply_costs_filter

    return rx.el.div(
        rx.el.p(
            "Filter by Costs",
            class_name="text-xs font-semibold text-gray-500 px-3 pt-2 pb-1",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Min cost",
                on_change=set_temp_min,
                class_name="w-full p-2 border border-gray-300 rounded text-sm mb-2 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                default_value=temp_min_cost_str,
            ),
            rx.el.input(
                placeholder="Max cost",
                on_change=set_temp_max,
                class_name="w-full p-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                default_value=temp_max_cost_str,
            ),
            class_name="p-2",
        ),
        rx.el.div(
            rx.el.button(
                "Reset",
                on_click=reset_filter,
                class_name="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded",
            ),
            rx.el.button(
                "Apply",
                on_click=apply_filter,
                class_name="px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded",
            ),
            class_name="flex justify-end space-x-2 p-2 border-t border-gray-200",
        ),
        class_name="absolute top-full left-0 mt-1 w-48 border border-gray-300 rounded z-10 bg-white shadow-lg",
        hidden=~show_filter,
    )


def filter_button(
    label: str,
    on_click: EventSpec,
    is_active: rx.Var[bool],
    has_filter: rx.Var[bool],
) -> rx.Component:
    """Generic filter button."""
    return rx.el.button(
        rx.el.span(
            rx.icon(tag="plus", size=14, class_name="mr-1"),
            label,
            class_name="flex items-center",
        ),
        rx.icon(tag="chevron_down", size=14, class_name="ml-1"),
        on_click=on_click,
        class_name=rx.cond(
            has_filter,
            "flex items-center px-3 py-1 border border-blue-300 rounded text-sm text-blue-700 bg-blue-50 hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1",
            "flex items-center px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1",
        ),
        aria_expanded=is_active,
    )


# Orders table filter dropdowns
def orders_province_filter_dropdown() -> rx.Component:
    """Dropdown component for filtering by Province in orders table."""
    return rx.el.div(
        rx.el.p(
            "Filter by Province",
            class_name="text-xs font-semibold text-gray-500 px-3 pt-2 pb-1",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.unique_provinces,
                lambda province: filter_checkbox_item(
                    label=province,
                    is_checked=DashboardState.orders_temp_selected_provinces.contains(province),
                    on_change=DashboardState.toggle_orders_temp_province,
                ),
            ),
            class_name="max-h-48 overflow-y-auto p-1",
        ),
        rx.el.div(
            rx.el.button(
                "Reset",
                on_click=DashboardState.reset_orders_province_filter,
                class_name="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded",
            ),
            rx.el.button(
                "Apply",
                on_click=DashboardState.apply_orders_province_filter,
                class_name="px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded",
            ),
            class_name="flex justify-end space-x-2 p-2 border-t border-gray-200",
        ),
        class_name="absolute top-full left-0 mt-1 w-56 border border-gray-300 rounded z-10 bg-white shadow-lg",
        hidden=~DashboardState.show_orders_province_filter,
    )


def orders_product_filter_dropdown() -> rx.Component:
    """Dropdown component for filtering by Product in orders table."""
    return rx.el.div(
        rx.el.p(
            "Filter by Product",
            class_name="text-xs font-semibold text-gray-500 px-3 pt-2 pb-1",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.unique_products,
                lambda product: filter_checkbox_item(
                    label=product,
                    is_checked=DashboardState.orders_temp_selected_products.contains(product),
                    on_change=DashboardState.toggle_orders_temp_product,
                ),
            ),
            class_name="max-h-48 overflow-y-auto p-1",
        ),
        rx.el.div(
            rx.el.button(
                "Reset",
                on_click=DashboardState.reset_orders_product_filter,
                class_name="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded",
            ),
            rx.el.button(
                "Apply",
                on_click=DashboardState.apply_orders_product_filter,
                class_name="px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded",
            ),
            class_name="flex justify-end space-x-2 p-2 border-t border-gray-200",
        ),
        class_name="absolute top-full left-0 mt-1 w-56 border border-gray-300 rounded z-10 bg-white shadow-lg",
        hidden=~DashboardState.show_orders_product_filter,
    )


def orders_revenue_filter_dropdown() -> rx.Component:
    """Dropdown component for filtering by Revenue in orders table."""
    return rx.el.div(
        rx.el.p(
            "Filter by Revenue",
            class_name="text-xs font-semibold text-gray-500 px-3 pt-2 pb-1",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Min revenue",
                on_change=DashboardState.set_orders_temp_min_revenue,
                class_name="w-full p-2 border border-gray-300 rounded text-sm mb-2 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                default_value=DashboardState.orders_temp_min_revenue_str,
            ),
            rx.el.input(
                placeholder="Max revenue",
                on_change=DashboardState.set_orders_temp_max_revenue,
                class_name="w-full p-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                default_value=DashboardState.orders_temp_max_revenue_str,
            ),
            class_name="p-2",
        ),
        rx.el.div(
            rx.el.button(
                "Reset",
                on_click=DashboardState.reset_orders_revenue_filter,
                class_name="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded",
            ),
            rx.el.button(
                "Apply",
                on_click=DashboardState.apply_orders_revenue_filter,
                class_name="px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded",
            ),
            class_name="flex justify-end space-x-2 p-2 border-t border-gray-200",
        ),
        class_name="absolute top-full left-0 mt-1 w-48 border border-gray-300 rounded z-10 bg-white shadow-lg",
        hidden=~DashboardState.show_orders_revenue_filter,
    )
