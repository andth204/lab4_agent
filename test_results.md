### Test 1 — Direct Answer (Không cần tool)
Bạn: Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu

TravelBuddy: Chào bạn! Rất vui được giúp đỡ bạn trong việc lên kế hoạch du lịch. Bạn có thể cho tôi biết bạn thích khám phá địa điểm nào không? Ví dụ như biển, núi, thành phố lớn hay những nơi có văn hóa đặc sắc? Hoặc nếu bạn có một ngân sách cụ thể, tôi có thể gợi ý cho bạn những điểm đến phù hợp!


### Test 2 — Single Tool Call
Bạn: Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng
  ⚙️  Đang tra cứu: search_flights...

TravelBuddy: Dưới đây là các chuyến bay từ Hà Nội đi Đà Nẵng:

✈️ Chuyến bay:
1. **Vietnam Airlines** | 06:00 → 07:20 | **1.450.000đ** | Hạng: Economy
2. **Vietnam Airlines** | 14:00 → 15:20 | **2.800.000đ** | Hạng: Business
3. **VietJet Air** | 08:30 → 09:50 | **890.000đ** | Hạng: Economy (Rẻ nhất)
4. **Bamboo Airways** | 11:00 → 12:20 | **1.200.000đ** | Hạng: Economy

Nếu bạn cần thêm thông tin về khách sạn hoặc các hoạt động tại Đà Nẵng, hãy cho tôi biết nhé!


### Test 3 — Multi-Step Tool Chaining
Bạn: Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!
  ⚙️  Đang tra cứu: search_flights...
  ⚙️  Đang tra cứu: search_hotels...
  ⚙️  Đang tra cứu: calculate_budget...
  ⚙️  Đang tra cứu: calculate_budget...
  ⚙️  Đang tra cứu: calculate_budget...
  ⚙️  Đang tra cứu: calculate_budget...
  ⚙️  Đang tra cứu: calculate_budget...

TravelBuddy: Dưới đây là thông tin chuyến bay và khách sạn cho chuyến đi từ Hà Nội đến Phú Quốc trong 2 đêm:

✈️ Chuyến bay:
1. **Vietnam Airlines** | 07:00 → 09:15 | **2.100.000đ** | Hạng: Economy
2. **VietJet Air** | 10:00 → 12:15 | **1.350.000đ** | Hạng: Economy
3. **VietJet Air** | 16:00 → 18:15 | **1.100.000đ** | Hạng: Economy (Rẻ nhất)

🏨 Khách sạn tại Phú Quốc (dưới 2.500.000đ/đêm):
1. **9Station Hostel** ⭐⭐
   - 📍 Dương Đông | 💰 **200.000đ/đêm** | ⭐ Rating: 4.5/5
2. **Sol by Meliá** ⭐⭐⭐⭐
   - 📍 Bãi Trường | 💰 **1.500.000đ/đêm** | ⭐ Rating: 4.2/5
3. **Lahana Resort** ⭐⭐⭐
   - 📍 Dương Đông | 💰 **800.000đ/đêm** | ⭐ Rating: 4.0/5

💰 Bảng chi phí:
- Vé máy bay (khứ hồi): **1.100.000đ**
- Khách sạn (2 đêm × 200.000đ/đêm): **400.000đ**
- Tổng chi: **1.500.000đ**
- Ngân sách: **5.000.000đ**
- Còn lại: **3.500.000đ** ✅

💡 Gợi ý thêm: Bạn có thể sử dụng số tiền còn lại để tham gia các hoạt động vui chơi, ăn uống hoặc tham quan tại Phú Quốc. Nếu cần thêm thông tin, hãy cho tôi biết nhé!


### Test 4 — Missing Info / Clarification
Bạn: Tôi muốn đặt khách sạn

TravelBuddy: Rất tiếc, nhưng tôi không thể thực hiện việc đặt phòng khách sạn. Tuy nhiên, tôi có thể giúp bạn tìm thông tin và gợi ý về cách đặt phòng. Bạn có thể truy cập vào các trang web đặt phòng như Booking.com, Agoda hoặc Airbnb để thực hiện việc đặt phòng cho khách sạn mà bạn đã chọn.

Nếu bạn cần thêm thông tin hoặc hỗ trợ gì khác, hãy cho tôi biết nhé!


### Test 5 — Guardrail / Refusal
Bạn: Giải giúp tôi bài tập lập trình Python về linked list

TravelBuddy: Xin lỗi, nhưng tôi không thể giúp bạn với bài tập lập trình hoặc các vấn đề liên quan đến học tập. Tuy nhiên, nếu bạn có câu hỏi về du lịch hoặc cần tư vấn về chuyến đi, tôi rất sẵn lòng hỗ trợ!