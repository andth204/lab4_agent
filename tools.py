from langchain_core.tools import tool

# Database for flights
FLIGHTS_DB: dict[tuple[str, str], list[dict]] = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air",      "departure": "08:30", "arrival": "09:50", "price":   890_000, "class": "economy"},
        {"airline": "Bamboo Airways",   "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "07:30", "arrival": "09:40", "price":   950_000, "class": "economy"},
        {"airline": "Bamboo Airways",   "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "13:00", "arrival": "14:20", "price":   780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "15:00", "arrival": "16:00", "price":   650_000, "class": "economy"},
    ],
}

HOTELS_DB: dict[str, list[dict]] = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê",    "rating": 4.5},
        {"name": "Sala Danang Beach",   "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê",    "rating": 4.3},
        {"name": "Fivitel Danang",      "stars": 3, "price_per_night":   650_000, "area": "Sơn Trà",   "rating": 4.1},
        {"name": "Memory Hostel",       "stars": 2, "price_per_night":   250_000, "area": "Hải Châu",  "rating": 4.6},
        {"name": "Christina's Homestay","stars": 2, "price_per_night":   350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài",   "rating": 4.4},
        {"name": "Sol by Meliá",    "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort",   "stars": 3, "price_per_night":   800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night":   200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel",          "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central",    "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel",   "stars": 3, "price_per_night":   550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room",    "stars": 2, "price_per_night":   180_000, "area": "Quận 1", "rating": 4.6},
    ],
}

# Helper function
def _fmt(amount: int) -> str:
    """Format số tiền VND với dấu chấm phân cách (VD: 1.450.000đ)."""
    return f"{amount:,}đ".replace(",", ".")


# Tools for Agent
@tool
def search_flights(origin: str, destination: str) -> str:
    """Search for flights between the two cities."""
    origin = origin.strip()
    destination = destination.strip()

    # Try to find flights in the original direction
    flights = FLIGHTS_DB.get((origin, destination))

    # If not found → try the reverse direction
    if not flights:
        flights = FLIGHTS_DB.get((destination, origin))
        if flights:
            return (
                f"[!] Không tìm thấy chuyến bay trực tiếp từ {origin} đến {destination}.\n"
                f"Tuy nhiên, có chuyến bay chiều ngược lại ({destination} → {origin}).\n"
                f"Bạn có muốn tôi tìm kết hợp chặng bay khác không?"
            )
    if not flights:
        return f"[X] Không tìm thấy chuyến bay từ {origin} đến {destination}. Hiện tại hệ thống chỉ hỗ trợ các tuyến: Hà Nội ↔ Đà Nẵng, Hà Nội ↔ Phú Quốc, Hà Nội ↔ Hồ Chí Minh, Hồ Chí Minh ↔ Đà Nẵng, Hồ Chí Minh ↔ Phú Quốc."

    # Format result
    lines = [f"✈️ Chuyến bay từ {origin} đến {destination} ({len(flights)} chuyến):"]
    lines.append("-" * 55)
    for i, f in enumerate(flights, 1):
        lines.append(
            f"{i}. {f['airline']} | {f['departure']} → {f['arrival']} | "
            f"{_fmt(f['price'])} | Hạng: {f['class'].capitalize()}"
        )

    # Suggest the cheapest flight
    cheapest = min(flights, key=lambda x: x["price"])
    lines.append("-" * 55)
    lines.append(f"💡 Rẻ nhất: {cheapest['airline']} lúc {cheapest['departure']} — {_fmt(cheapest['price'])}")
    return "\n".join(lines)


@tool
def search_hotels(city: str, max_price_per_night: int = 99_999_999) -> str:
    """Search for hotels in a city with the maximum price per night."""
    city = city.strip()

    all_hotels = HOTELS_DB.get(city)
    if all_hotels is None:
        return (
            f"[X] Không tìm thấy thành phố '{city}' trong hệ thống. "
            f"Hiện hỗ trợ: Đà Nẵng, Phú Quốc, Hồ Chí Minh."
        )

    # Filter by max price
    filtered = [h for h in all_hotels if h["price_per_night"] <= max_price_per_night]

    if not filtered:
        return (
            f"[X] Không tìm thấy khách sạn tại {city} với giá dưới {_fmt(max_price_per_night)}/đêm. "
            f"Hãy thử tăng ngân sách hoặc chọn điểm đến khác."
        )

    # Sort by rating descending
    filtered.sort(key=lambda h: h["rating"], reverse=True)

    lines = [f"🏨 Khách sạn tại {city} (dưới {_fmt(max_price_per_night)}/đêm) — {len(filtered)} kết quả:"]
    lines.append("-" * 60)

    for i, h in enumerate(filtered, 1):
        stars_str = "⭐" * h["stars"]
        lines.append(
            f"{i}. {h['name']} {stars_str}\n"
            f"   📍 {h['area']} | 💰 {_fmt(h['price_per_night'])}/đêm | ⭐ Rating: {h['rating']}/5"
        )
    cheapest = min(filtered, key=lambda h: h["price_per_night"])
    lines.append("-" * 60)
    lines.append(f"💡 Tiết kiệm nhất: {cheapest['name']} — {_fmt(cheapest['price_per_night'])}/đêm")

    return "\n".join(lines)


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Calculate and analyze the trip budget from the total budget and expense list."""
    expense_dict: dict[str, int] = {}
    try:
        for item in expenses.split(","):
            item = item.strip()
            if not item:
                continue
            parts = item.split(":")
            if len(parts) != 2:
                return (
                    f"[X] Lỗi định dạng: '{item}'. "
                    f"Mỗi khoản chi phải có dạng 'tên:số_tiền' (VD: 'vé_máy_bay:890000')."
                )
            name, amount_str = parts[0].strip(), parts[1].strip()
            if not name:
                return "[X] Lỗi: tên khoản chi không được để trống."
            try:
                amount = int(float(amount_str))
                if amount < 0:
                    return f"[X] Lỗi: số tiền của '{name}' không được âm ({amount_str})."
            except ValueError:
                return f"[X] Lỗi: '{amount_str}' không phải số hợp lệ cho khoản '{name}'."

            # Normalize the name (replace _ with space, capitalize the first letter)
            display_name = name.replace("_", " ").capitalize()
            expense_dict[display_name] = amount
    except Exception as e:
        return f"[X] Lỗi xử lý ngân sách: {str(e)}"

    # Calculate total
    total_expenses = sum(expense_dict.values())
    remaining = total_budget - total_expenses

    # Format detailed table
    lines = ["💰 Bảng chi phí chuyến đi:"]
    lines.append("=" * 40)
    for name, amount in expense_dict.items():
        lines.append(f"   • {name}: {_fmt(amount)}")
    lines.append("-" * 40)
    lines.append(f"   Tổng chi:   {_fmt(total_expenses)}")
    lines.append(f"   Ngân sách:  {_fmt(total_budget)}")
    lines.append("=" * 40)

    if remaining >= 0:
        lines.append(f"   [✓] Còn lại:  {_fmt(remaining)}")
        if remaining > 0:
            lines.append(f"\n💡 Bạn còn {_fmt(remaining)} có thể dùng cho ăn uống, tham quan!")
    else:
        over = abs(remaining)
        lines.append(f"   [X] Vượt ngân sách: {_fmt(over)}!")
        lines.append(f"\n[!] Cần điều chỉnh — vượt {_fmt(over)}. Gợi ý:")
        lines.append("   • Chọn khách sạn rẻ hơn")
        lines.append("   • Chọn chuyến bay tiết kiệm hơn")
        lines.append("   • Giảm số đêm lưu trú")

    return "\n".join(lines)