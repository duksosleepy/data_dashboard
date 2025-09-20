import reflex as rx

config = rx.Config(
    app_name="data_dashboard",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    frontend_port=3035,
    backend_port=8035,
)
