const Research = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-4">Nghiên cứu & Phát triển</h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            VCareMind được xây dựng dựa trên nền tảng nghiên cứu khoa học vững chắc về 
            sức khỏe tinh thần người cao tuổi và ứng dụng công nghệ AI trong chăm sóc y tế.
          </p>
        </div>

        {/* Main Research Paper */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-primary to-primary-accent p-8 rounded-lg text-white mb-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-2xl">📋</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold">Báo cáo nghiên cứu chính</h2>
                <p className="text-white/90">VCareMind - Ứng dụng chăm sóc tinh thần người cao tuổi với trợ lý ảo đồng hành</p>
              </div>
            </div>
            
            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold">50</div>
                <div className="text-white/80">Người tham gia</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">95%</div>
                <div className="text-white/80">Tỷ lệ hài lòng</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">6</div>
                <div className="text-white/80">Tháng nghiên cứu</div>
              </div>
            </div>

            <a 
              href="https://drive.google.com/file/d/1v9giq6Zs4A-Q7WYelHXY1ZfGNq__d1oo/edit" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-block bg-white text-primary px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Xem báo cáo đầy đủ
            </a>
          </div>
        </section>

        {/* Research Methodology */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8">🔬 Phương pháp nghiên cứu</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-blue-500">👥</span>
                Đối tượng nghiên cứu
              </h3>
              <ul className="space-y-2 text-gray-600">
                <li>• <strong>30 người cao tuổi</strong> (65-98 tuổi)</li>
                <li>• <strong>20 caregiver</strong> (con cháu, người thân)</li>
                <li>• 90% có bệnh mãn tính</li>
                <li>• Đa số sử dụng smartphone hàng ngày</li>
                <li>• Phân bố đều giữa thành thị và nông thôn</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-green-500">📊</span>
                Quy trình đánh giá
              </h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Pre-test survey & observation</li>
                <li>• In-test interaction với các tính năng</li>
                <li>• Post-test interview chi tiết</li>
                <li>• Theo dõi dài hạn (4-6 tuần)</li>
                <li>• Phân tích định lượng và định tính</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Key Findings */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8">📈 Kết quả nghiên cứu chính</h2>
          
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-6">Hiệu quả với người cao tuổi:</h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-green-50 p-6 rounded-lg text-center border border-green-200">
                <div className="text-3xl font-bold text-green-600 mb-2">95%</div>
                <div className="text-sm text-gray-600">Thấy dễ dùng & hữu ích</div>
              </div>
              <div className="bg-blue-50 p-6 rounded-lg text-center border border-blue-200">
                <div className="text-3xl font-bold text-blue-600 mb-2">40%</div>
                <div className="text-sm text-gray-600">Giảm cảm giác cô đơn</div>
              </div>
              <div className="bg-purple-50 p-6 rounded-lg text-center border border-purple-200">
                <div className="text-3xl font-bold text-purple-600 mb-2">85%</div>
                <div className="text-sm text-gray-600">Tuân thủ uống thuốc tốt hơn</div>
              </div>
              <div className="bg-orange-50 p-6 rounded-lg text-center border border-orange-200">
                <div className="text-3xl font-bold text-orange-600 mb-2">1-2s</div>
                <div className="text-sm text-gray-600">Thời gian phản hồi</div>
              </div>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-6">Tác động với gia đình:</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                <h4 className="font-semibold mb-3 text-primary">Giảm lo lắng</h4>
                <p className="text-gray-600 text-sm">
                  95% caregiver cảm thấy yên tâm hơn khi chăm sóc từ xa, 
                  nhờ khả năng theo dõi tình trạng sức khỏe real-time.
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                <h4 className="font-semibold mb-3 text-primary">Tiết kiệm thời gian</h4>
                <p className="text-gray-600 text-sm">
                  Giảm 60% thời gian gọi điện nhắc nhở, 
                  tăng chất lượng thời gian tương tác với người thân.
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                <h4 className="font-semibold mb-3 text-primary">Kết nối gia đình</h4>
                <p className="text-gray-600 text-sm">
                  Tính năng hồi ký giúp các thế hệ hiểu nhau hơn, 
                  tăng cường gắn kết gia đình.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* User Testimonials */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8">💬 Phản hồi từ người dùng</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-blue-200 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 font-bold">👵</span>
                </div>
                <div>
                  <div className="font-semibold">Bà Nguyễn Thị H., 78 tuổi</div>
                  <div className="text-sm text-gray-600">Hà Nội</div>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "Cháu ơi, có VCareMind thì bà bớt cô đơn lắm. Nó nhắc bà uống thuốc, 
                còn trò chuyện rất dễ thương. Giống như có người bạn ở bên vậy."
              </p>
            </div>

            <div className="bg-green-50 p-6 rounded-lg border border-green-200">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-green-200 rounded-full flex items-center justify-center">
                  <span className="text-green-600 font-bold">👨</span>
                </div>
                <div>
                  <div className="font-semibold">Anh Trần Văn M., 45 tuổi</div>
                  <div className="text-sm text-gray-600">Con trai, TP.HCM</div>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "Tôi yên tâm hơn nhiều khi làm việc xa nhà. VCareMind giúp tôi theo dõi 
                tình trạng bố mẹ, và họ cũng thích nghe những câu chuyện cũ được nhắc lại."
              </p>
            </div>
          </div>
        </section>

        {/* Research Insights */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8">💡 Insights quan trọng</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
              <h3 className="font-semibold mb-3 text-yellow-700">Thói quen sử dụng</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Sử dụng chủ yếu vào buổi sáng và tối</li>
                <li>• Thích nghe hơn là đọc</li>
                <li>• Cần thời gian làm quen (2-3 ngày)</li>
                <li>• Ưa thích giọng nói thân thiện, chậm rãi</li>
              </ul>
            </div>

            <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
              <h3 className="font-semibold mb-3 text-purple-700">Rào cản công nghệ</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 5% ngại sử dụng công nghệ mới</li>
                <li>• Cần hướng dẫn từ con cháu</li>
                <li>• Thích giao diện đơn giản, nút to</li>
                <li>• Quan tâm về quyền riêng tư</li>
              </ul>
            </div>

            <div className="bg-red-50 p-6 rounded-lg border border-red-200">
              <h3 className="font-semibold mb-3 text-red-700">Nhu cầu chưa được đáp ứng</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Kết nối với bác sĩ trực tiếp</li>
                <li>• Cảnh báo khẩn cấp tự động</li>
                <li>• Hỗ trợ đa ngôn ngữ (tiếng địa phương)</li>
                <li>• Tích hợp với thiết bị y tế</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Scientific Publications */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8">📚 Công bố khoa học</h2>
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-primary text-xl">📄</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-2">
                    "AI Voice Assistant for Mental Health Support in Vietnamese Elderly: A Randomized Controlled Trial"
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Journal of Medical Internet Research (JMIR) - Under Review
                  </p>
                  <p className="text-sm text-gray-700">
                    Nghiên cứu đầu tiên tại Việt Nam về hiệu quả của trợ lý ảo giọng nói 
                    trong việc hỗ trợ sức khỏe tinh thần người cao tuổi.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600 text-xl">📊</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-2">
                    "Digital Health Solutions for Aging Population in Southeast Asia"
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Asian Journal of Gerontology & Geriatrics - Published 2024
                  </p>
                  <p className="text-sm text-gray-700">
                    Tổng quan về các giải pháp chăm sóc sức khỏe số cho người cao tuổi 
                    tại khu vực Đông Nam Á.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Future Research */}
        <section className="bg-gradient-to-r from-blue-50 to-green-50 p-8 rounded-lg">
          <h2 className="text-2xl font-bold mb-6">🔮 Hướng nghiên cứu tương lai</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold mb-4">Nghiên cứu đang triển khai</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Ứng dụng AI trong dự báo sớm trầm cảm</li>
                <li>• Tích hợp với thiết bị IoT và wearable</li>
                <li>• Phân tích ngôn ngữ để đánh giá sa sút trí tuệ</li>
                <li>• Mở rộng ra các quốc gia ASEAN</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-4">Kế hoạch 2025-2026</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Nghiên cứu đa trung tâm với 1000 NCT</li>
                <li>• Hợp tác với WHO về tiêu chuẩn quốc tế</li>
                <li>• Phát triển mô hình AI dự đoán nguy cơ</li>
                <li>• Ứng dụng blockchain trong bảo mật y tế</li>
              </ul>
            </div>
          </div>
          
          <div className="text-center mt-8">
            <p className="mb-4 text-gray-600">Quan tâm đến việc hợp tác nghiên cứu?</p>
            <a 
              href="mailto:ngthuyn22@gmail.com?subject=Hợp tác nghiên cứu VCareMind"
              className="inline-block bg-primary text-white px-8 py-3 rounded-lg hover:bg-primary/90 transition-colors font-medium"
            >
              Liên hệ nghiên cứu
            </a>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Research;