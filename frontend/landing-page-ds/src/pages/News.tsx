const News = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-3xl font-bold mb-8">Tin tức & Cập nhật</h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Featured News */}
          <div className="md:col-span-2 lg:col-span-3">
            <div className="bg-gradient-to-r from-primary to-primary-accent p-8 rounded-lg text-white mb-8">
              <div className="flex items-center gap-2 mb-4">
                <span className="bg-white text-primary px-3 py-1 rounded-full text-sm font-medium">
                  Nổi bật
                </span>
                <span className="text-white/80">15/12/2024</span>
              </div>
              <h2 className="text-2xl font-bold mb-4">
                VCareMind đạt tỷ lệ hài lòng 95% từ người dùng thử nghiệm
              </h2>
              <p className="mb-4 text-white/90">
                Sau 6 tháng thử nghiệm với 50 người cao tuổi và gia đình, VCareMind đã chứng minh 
                hiệu quả trong việc giảm cô đơn và hỗ trợ tuân thủ điều trị.
              </p>
              <a href="#" className="inline-block bg-white text-primary px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Đọc chi tiết
              </a>
            </div>
          </div>

          {/* News Grid */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">Sản phẩm</span>
                <span className="text-gray-500 text-sm">12/12/2024</span>
              </div>
              <h3 className="text-lg font-semibold mb-3">
                Ra mắt tính năng quét đơn thuốc tự động
              </h3>
              <p className="text-gray-600 mb-4">
                Người cao tuổi giờ đây có thể chụp đơn thuốc từ bác sĩ để tự động thiết lập lịch nhắc uống thuốc.
              </p>
              <a href="#" className="text-primary font-medium hover:underline">Xem thêm →</a>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Nghiên cứu</span>
                <span className="text-gray-500 text-sm">10/12/2024</span>
              </div>
              <h3 className="text-lg font-semibold mb-3">
                Báo cáo: AI giảm 40% cảm giác cô đơn ở người cao tuổi
              </h3>
              <p className="text-gray-600 mb-4">
                Nghiên cứu độc lập cho thấy trợ lý ảo giọng nói có tác động tích cực đến sức khỏe tinh thần.
              </p>
              <a href="#" className="text-primary font-medium hover:underline">Xem thêm →</a>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-sm">Hợp tác</span>
                <span className="text-gray-500 text-sm">08/12/2024</span>
              </div>
              <h3 className="text-lg font-semibold mb-3">
                Ký kết hợp tác với Bệnh viện Lão khoa Trung ương
              </h3>
              <p className="text-gray-600 mb-4">
                VCareMind chính thức trở thành đối tác công nghệ trong chương trình chăm sóc sức khỏe người cao tuổi.
              </p>
              <a href="#" className="text-primary font-medium hover:underline">Xem thêm →</a>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded text-sm">Giải thưởng</span>
                <span className="text-gray-500 text-sm">05/12/2024</span>
              </div>
              <h3 className="text-lg font-semibold mb-3">
                VCareMind đoạt giải Nhất cuộc thi "Đổi mới sáng tạo vì cộng đồng"
              </h3>
              <p className="text-gray-600 mb-4">
                Được Bộ Khoa học & Công nghệ vinh danh về ứng dụng AI trong chăm sóc người cao tuổi.
              </p>
              <a href="#" className="text-primary font-medium hover:underline">Xem thêm →</a>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-sm">Cộng đồng</span>
                <span className="text-gray-500 text-sm">03/12/2024</span>
              </div>
              <h3 className="text-lg font-semibold mb-3">
                Chương trình "VCareMind cho mọi nhà" tại vùng nông thôn
              </h3>
              <p className="text-gray-600 mb-4">
                Triển khai miễn phí ứng dụng cho 1000 người cao tuổi tại các tỉnh miền núi phía Bắc.
              </p>
              <a href="#" className="text-primary font-medium hover:underline">Xem thêm →</a>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">Cập nhật</span>
                <span className="text-gray-500 text-sm">01/12/2024</span>
              </div>
              <h3 className="text-lg font-semibold mb-3">
                Phiên bản 2.0 với giao diện mới và nhiều tính năng
              </h3>
              <p className="text-gray-600 mb-4">
                Cải thiện trải nghiệm người dùng với giao diện đơn giản hơn và thời gian phản hồi nhanh hơn.
              </p>
              <a href="#" className="text-primary font-medium hover:underline">Xem thêm →</a>
            </div>
          </div>
        </div>

        {/* Newsletter Signup */}
        <div className="bg-gradient-to-r from-blue-50 to-green-50 p-8 rounded-lg mt-12">
          <div className="max-w-2xl mx-auto text-center">
            <h3 className="text-2xl font-bold mb-4">Nhận tin tức mới nhất</h3>
            <p className="text-gray-600 mb-6">
              Đăng ký để cập nhật những tin tức, tính năng mới và các nghiên cứu về chăm sóc người cao tuổi.
            </p>
            <div className="flex gap-4 max-w-md mx-auto">
              <input 
                type="email" 
                placeholder="Nhập email của bạn"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <button className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 transition-colors">
                Đăng ký
              </button>
            </div>
          </div>
        </div>

        {/* Media Coverage */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold mb-8">Báo chí nói về VCareMind</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary mb-2">VnExpress</div>
              <p className="text-sm text-gray-600">"Giải pháp AI tiên phong cho người cao tuổi Việt Nam"</p>
            </div>
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary mb-2">Tuổi Trẻ</div>
              <p className="text-sm text-gray-600">"Ứng dụng được người cao tuổi yêu thích nhất"</p>
            </div>
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary mb-2">VTV</div>
              <p className="text-sm text-gray-600">"Công nghệ vì sức khỏe cộng đồng"</p>
            </div>
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary mb-2">Thanh Niên</div>
              <p className="text-sm text-gray-600">"Startup Việt chinh phục thị trường lão hóa"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default News;