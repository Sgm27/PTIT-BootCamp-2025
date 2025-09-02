const UserGuide = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Hướng dẫn sử dụng VCareMind</h1>
        
        <div className="prose prose-lg max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">🚀 Bắt đầu với VCareMind</h2>
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-xl font-medium mb-3">Bước 1: Tải và cài đặt ứng dụng</h3>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Quét mã QR hoặc truy cập link tải xuống</li>
                <li>Cài đặt file APK trên thiết bị Android</li>
                <li>Mở ứng dụng và tạo tài khoản</li>
                <li>Cấp quyền microphone và camera khi được yêu cầu</li>
              </ol>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">🗣️ Sử dụng trợ lý giọng nói</h2>
            <div className="bg-green-50 p-6 rounded-lg">
              <h3 className="text-xl font-medium mb-3">Cách trò chuyện với VCareMind:</h3>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Nhấn nút microphone màu xanh để bắt đầu</li>
                <li>Nói chậm rãi và rõ ràng</li>
                <li>Chờ phản hồi từ trợ lý (1-2 giây)</li>
                <li>Có thể hỏi về sức khỏe, chia sẻ cảm xúc, kể chuyện</li>
              </ol>
              <p className="mt-4 text-sm text-gray-600">
                <strong>Mẹo:</strong> Đặt điện thoại ở vị trí gần và tăng âm lượng để nghe rõ hơn.
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">💊 Quản lý thuốc thông minh</h2>
            <div className="bg-yellow-50 p-6 rounded-lg">
              <h3 className="text-xl font-medium mb-3">Quét và nhận diện thuốc:</h3>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Nhấn vào biểu tượng camera</li>
                <li>Chụp rõ ràng hộp thuốc hoặc vỉ thuốc</li>
                <li>Chờ hệ thống nhận diện và hiển thị thông tin</li>
                <li>Xem công dụng, liều lượng và cách sử dụng</li>
              </ol>
              
              <h3 className="text-xl font-medium mb-3 mt-6">Thiết lập lịch nhắc thuốc:</h3>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Vào mục "Lịch uống thuốc"</li>
                <li>Thêm tên thuốc và thời gian uống</li>
                <li>Chọn tần suất (hàng ngày, theo ngày trong tuần)</li>
                <li>Bật thông báo âm thanh</li>
              </ol>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">👨‍👩‍👧‍👦 Kết nối với gia đình</h2>
            <div className="bg-purple-50 p-6 rounded-lg">
              <h3 className="text-xl font-medium mb-3">Dành cho người thân/con cháu:</h3>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Tải ứng dụng VCareMind Caregiver</li>
                <li>Liên kết với tài khoản của người cao tuổi</li>
                <li>Theo dõi tình trạng sức khỏe từ xa</li>
                <li>Nhận thông báo về lịch uống thuốc</li>
                <li>Xem báo cáo hoạt động hàng tuần</li>
              </ol>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">📝 Tính năng hồi ký</h2>
            <div className="bg-pink-50 p-6 rounded-lg">
              <h3 className="text-xl font-medium mb-3">Lưu giữ kỷ niệm bằng giọng nói:</h3>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Kể câu chuyện, ký ức với trợ lý ảo</li>
                <li>Hệ thống tự động ghi nhận và lưu trữ</li>
                <li>Trợ lý sẽ nhắc lại những câu chuyện này</li>
                <li>Có thể chia sẻ với con cháu (khi đồng ý)</li>
              </ol>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">⚙️ Cài đặt và tùy chỉnh</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Âm lượng:</strong> Điều chỉnh âm lượng phù hợp với thính lực</li>
              <li><strong>Giọng đọc:</strong> Chọn giọng nam/nữ, tốc độ nói</li>  
              <li><strong>Ngôn ngữ:</strong> Hỗ trợ tiếng Việt với nhiều giọng địa phương</li>
              <li><strong>Thông báo:</strong> Bật/tắt các loại thông báo</li>
              <li><strong>Bảo mật:</strong> Thiết lập mật khẩu, xác thực sinh trắc học</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">🆘 Xử lý sự cố</h2>
            <div className="bg-red-50 p-6 rounded-lg">
              <h3 className="text-xl font-medium mb-3">Các vấn đề thường gặp:</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Không nghe được giọng nói:</strong> Kiểm tra âm lượng, microphone</li>
                <li><strong>Trợ lý không hiểu:</strong> Nói chậm hơn, rõ ràng hơn</li>
                <li><strong>Ứng dụng bị lỗi:</strong> Khởi động lại ứng dụng</li>
                <li><strong>Quên mật khẩu:</strong> Sử dụng tính năng "Quên mật khẩu"</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">📞 Hỗ trợ kỹ thuật</h2>
            <p>Nếu cần hỗ trợ, vui lòng liên hệ:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Hotline: 0374829059 (8:00 - 18:00 hàng ngày)</li>
              <li>Email: ngthuyn22@gmail.com</li>
              <li>Thời gian phản hồi: Trong vòng 24 giờ</li>
            </ul>
          </section>

          <div className="bg-blue-100 p-6 rounded-lg mt-8">
            <h3 className="text-xl font-medium mb-3">💡 Lời khuyên sử dụng hiệu quả</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Sử dụng thường xuyên để trợ lý hiểu bạn better</li>
              <li>Chia sẻ cảm xúc và tâm trạng hàng ngày</li>
              <li>Thiết lập lịch trình cố định cho thuốc và hoạt động</li>
              <li>Kết nối với con cháu để họ yên tâm hơn</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserGuide;