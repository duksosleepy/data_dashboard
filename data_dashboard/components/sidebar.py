import reflex as rx

from data_dashboard.states.dashboard_state import DashboardState


def sidebar_item(
    text: str,
    icon: str,
    section_id: str,
    is_active: bool = False,
) -> rx.Component:
    """A reusable sidebar item component."""
    return rx.el.a(
        rx.icon(tag=icon, class_name="mr-3 size-4"),
        rx.el.label(text, class_name="text-sm"),
        on_click=lambda: DashboardState.set_selected_section(section_id),
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-gray-100 rounded-lg cursor-pointer",
            "flex items-center px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-lg cursor-pointer",
        ),
    )


def sidebar() -> rx.Component:
    """The sidebar component for the dashboard."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.img(
                        src="/logo.png",
                        alt="Logo",
                        class_name="h-6 w-6 mr-2",
                    ),
                    rx.el.label(
                        "LUG.vn",
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.label(
                    "v.0.0.1",
                    class_name="text-sm font-regular text-gray-500",
                ),
                class_name="flex items-center px-2 h-12 justify-between",
            ),
            rx.el.label(
                "Projects",
                class_name="px-4 mb-2 text-sm font-semibold tracking-wider text-gray-500 uppercase",
            ),
            rx.el.nav(
                sidebar_item(
                    "Overview",
                    "layout-dashboard",
                    "overview",
                    is_active=DashboardState.selected_section == "overview",
                ),
                sidebar_item(
                    "Data",
                    "database",
                    "data",
                    is_active=DashboardState.selected_section == "data",
                ),
                class_name="space-y-1",
            ),
        ),
        class_name="max-md:hidden flex flex-col justify-between w-[280px] h-screen px-2 bg-white border-r border-gray-200 sticky",
    )
