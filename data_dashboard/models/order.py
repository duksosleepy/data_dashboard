from typing import TypedDict


class OrderEntry(TypedDict):
    """Type definition for order data from DuckDB."""

    id: int
    order_date: str  # "Ngày Ct"
    document_type: str  # "Mã Ct"
    document_number: str  # "Số Ct"
    department_code: str  # "Mã bộ phận"
    order_id: str  # "Mã đơn hàng"
    customer_name: str  # "Tên khách hàng"
    phone_number: str  # "Số điện thoại"
    province: str  # "Tỉnh thành"
    district: str  # "Quận huyện"
    ward: str  # "Phường xã"
    address: str  # "Địa chỉ"
    product_code: str  # "Mã hàng"
    product_name: str  # "Tên hàng"
    imei: str  # "Imei"
    quantity: str  # "Số lượng"
    revenue: str  # "Doanh thu"
    error_code: str  # "Ghi chú"
