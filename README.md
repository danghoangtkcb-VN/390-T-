# Hành trình 390 câu đấu thầu

Ứng dụng HTML tiếng Việt, 13 chặng × 30 câu, Flashcard, luyện câu yếu, lưu tiến độ trên cùng trình duyệt/thiết bị. Đạt tối thiểu 90% số câu có đáp án để mở chặng sau. Không đồng bộ tiến độ giữa các máy.

## Chạy và triển khai

Yêu cầu Node.js 22 trở lên; không cần cài thư viện.

```sh
npm test
npm run build
npm start
```

Mở `http://localhost:3900`. Trên Vercel, nhập repo này, chọn Framework **Other**, Root Directory để mặc định. `vercel.json` đã cấu hình lệnh `npm run build` và thư mục đầu ra `dist`. Build tự giải nén 780 MP3 từ ZIP gốc, không phục vụ ZIP hoặc mã nguồn ra website.

## Âm thanh

Không dùng Web Speech API, không chọn giọng mặc định của hệ điều hành. Nút đọc dùng MP3, giữ cùng một phần tử audio qua câu hỏi → đáp án. Dừng/chuyển thẻ hủy lượt phát trước; tốc độ 0.8/1/1.2.

780 bản ghi trong ZIP chưa có metadata xác nhận giọng nam miền Bắc và có thể không khớp ghi chú nguồn đã cập nhật. Vì vậy chỉ nghe chúng khi bật lựa chọn bản ghi nguồn; mặc định không phát chúng. Không quảng bá những bản ghi này là giọng nam Bắc tự nhiên.

Để tạo bản ghi nam miền Bắc đã chỉ định rõ, dùng FPT voice `leminh` (theo https://docs.fpt.ai/docs/vi/speech/api/text-to-speech/). Cấu hình `FPT_API_KEY` trong môi trường riêng rồi chạy:

```sh
python3 scripts/generate_audio.py
npm run build
```

Script tạo câu hỏi và đáp án kèm phần ghi nhớ cho mỗi câu; ghi dấu vân tay nội dung để chạy tiếp sau khi gián đoạn. Manifest chỉ đánh dấu hoàn tất khi đủ 780 MP3. Lưu `audio/` vào git rồi triển khai lại. Khóa API không đưa vào client hoặc git. Việc tạo có thể tiêu thụ hạn mức dịch vụ; hiện chưa gọi dịch vụ vì chưa có khóa. Chưa kiểm chứng chất lượng nghe thực tế.

## Dữ liệu và các giới hạn

Giữ nguyên 390 câu trong ZIP tại commit gốc `ec11407`. 12 câu `NH032, NH034, NH080, NH194, NH207, NH260, NH266, NH271, NH273, NH277, BS016, BS040` chưa có đáp án duy nhất trong dữ liệu nguồn, nên hiển thị ghi chú và không chấm. Không tự ghi đè NH032 hoặc NH033. Đây là bảo toàn dữ liệu nguồn, không phải một lần xác minh pháp luật hiện hành độc lập.

30 câu có móc nhớ gốc. 360 câu còn lại dùng phần **gợi ý ôn tập tự động** từ đáp án và căn cứ nguồn, không gắn nhãn là móc nhớ được chuyên gia kiểm chứng.

## Kiểm thử

`npm test`: dữ liệu, trạng thái lưu hỏng, khóa chặng, tỉ lệ đạt chính xác, giữ thành tích khi thi lại, xáo câu, câu chưa chốt, phát nối tiếp, dừng âm thanh và tuyệt đối không rơi về giọng hệ thống. Đây là kiểm thử logic với DOM/audio mô phỏng, không phải kiểm thử thiết bị Android.

Cần thực hiện trước nghiệm thu trên Android thật: Chrome trên điện thoại → mở bản triển khai → Flashcard → đọc từng phần/toàn bộ → dừng/chuyển nhanh thẻ → xoay màn hình → đổi tốc độ → tải lại để kiểm tra lưu tiến độ → hoàn thành/chưa đạt một chặng → kiểm tra khóa chặng tiếp. Kiểm tra cả khi mất mạng và khi thiếu tệp MP3. Trình duyệt từ môi trường kiểm thử hiện tại không truy cập được máy chủ localhost; chưa có bằng chứng kiểm thử giao diện hoặc phát âm thanh trên Android thật.
