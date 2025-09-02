const FAQ = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Câu hỏi thường gặp (FAQ)</h1>
        
        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-6 text-primary">🔰 Về VCareMind</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-primary pl-6">
                <h3 className="text-lg font-medium mb-2">VCareMind là gì?</h3>
                <p className="text-gray-700">
                  VCareMind là ứng dụng trợ lý ảo sử dụng công nghệ AI và giọng nói tự nhiên, được thiết kế đặc biệt 
                  để hỗ trợ người cao tuổi trong việc chăm sóc sức khỏe tinh thần, nhắc nhở uống thuốc và duy trì kết nối với gia đình.
                </p>
              </div>
              
              <div className="border-l-4 border-primary pl-6">
                <h3 className="text-lg font-medium mb-2">VCareMind khác gì với các ứng dụng sức khỏe khác?</h3>
                <p className="text-gray-700">
                  VCareMind tập trung vào sức khỏe tinh thần, sử dụng giọng nói làm giao tiếp chính, có tính năng hồi ký tự động, 
                  và được thiết kế đặc biệt thân thiện với người cao tuổi.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6 text-green-600">📱 Cài đặt và sử dụng</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-green-500 pl-6">
                <h3 className="text-lg font-medium mb-2">VCareMind có hỗ trợ iPhone không?</h3>
                <p className="text-gray-700">
                  Hiện tại VCareMind chỉ hỗ trợ Android. Phiên bản iOS đang trong quá trình phát triển và sẽ sớm ra mắt.
                </p>
              </div>
              
              <div className="border-l-4 border-green-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Tôi không giỏi công nghệ, có sử dụng được không?</h3>
                <p className="text-gray-700">
                  Hoàn toàn có thể! VCareMind được thiết kế đặc biệt đơn giản, chủ yếu sử dụng giọng nói. 
                  Bạn chỉ cần nói, trợ lý sẽ hiểu và phản hồi bằng giọng nói.
                </p>
              </div>
              
              <div className="border-l-4 border-green-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Ứng dụng có cần kết nối internet không?</h3>
                <p className="text-gray-700">
                  Có, VCareMind cần kết nối internet để hoạt động. Tuy nhiên, một số tính năng cơ bản như nhắc thuốc 
                  vẫn hoạt động khi mất mạng tạm thời.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6 text-blue-600">🔒 Bảo mật và quyền riêng tư</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-blue-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Thông tin của tôi có được bảo mật không?</h3>
                <p className="text-gray-700">
                  Có, tất cả thông tin được mã hóa end-to-end và lưu trữ an toàn trên hệ thống AWS. 
                  Chúng tôi tuân thủ các tiêu chuẩn bảo mật quốc tế ISO 27001.
                </p>
              </div>
              
              <div className="border-l-4 border-blue-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Ai có thể nghe được cuộc trò chuyện của tôi?</h3>
                <p className="text-gray-700">
                  Chỉ có bạn và những người được bạn ủy quyền (như con cháu) mới có thể truy cập. 
                  Nhân viên VCareMind không thể nghe cuộc trò chuyện của bạn.
                </p>
              </div>
              
              <div className="border-l-4 border-blue-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Tôi có thể xóa dữ liệu của mình không?</h3>
                <p className="text-gray-700">
                  Có, bạn có thể yêu cầu xóa toàn bộ hoặc một phần dữ liệu bất kỳ lúc nào 
                  qua tính năng trong ứng dụng hoặc liên hệ hỗ trợ.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6 text-purple-600">💊 Về quản lý thuốc</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-purple-500 pl-6">
                <h3 className="text-lg font-medium mb-2">VCareMind có thể thay thế bác sĩ không?</h3>
                <p className="text-gray-700 font-medium text-red-600">
                  KHÔNG. VCareMind chỉ là công cụ hỗ trợ, không thay thế lời khuyên y tế chuyên nghiệp. 
                  Luôn tham khảo ý kiến bác sĩ về tình trạng sức khỏe.
                </p>
              </div>
              
              <div className="border-l-4 border-purple-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Nếu tôi quên uống thuốc, ứng dụng có nhắc không?</h3>
                <p className="text-gray-700">
                  Có, VCareMind sẽ nhắc nhở bằng giọng nói ở múi giờ bạn đã đặt. 
                  Nếu không phản hồi, sẽ có thông báo gửi đến người thân.
                </p>
              </div>
              
              <div className="border-l-4 border-purple-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Quét thuốc có chính xác không?</h3>
                <p className="text-gray-700">
                  Tính năng quét thuốc có độ chính xác cao với cơ sở dữ liệu từ drugbank.vn. 
                  Tuy nhiên, luôn kiểm tra với bác sĩ hoặc dược sĩ để chắc chắn.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6 text-orange-600">👨‍👩‍👧‍👦 Cho gia đình</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-orange-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Con cháu có thể theo dõi được gì?</h3>
                <p className="text-gray-700">
                  Con cháu có thể xem lịch uống thuốc, tình trạng sức khỏe tổng quan, báo cáo hoạt động, 
                  và nhận cảnh báo khi cần thiết (với sự đồng ý của người cao tuổi).
                </p>
              </div>
              
              <div className="border-l-4 border-orange-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Làm sao kết nối với tài khoản cha/mẹ?</h3>
                <p className="text-gray-700">
                  Tải ứng dụng VCareMind Caregiver, nhập mã kết nối do cha/mẹ cung cấp, 
                  và xác nhận kết nối qua số điện thoại.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6 text-red-600">💰 Chi phí</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-red-500 pl-6">
                <h3 className="text-lg font-medium mb-2">VCareMind có miễn phí không?</h3>
                <p className="text-gray-700">
                  Có gói miễn phí với các tính năng cơ bản như nhắc thuốc, trò chuyện đơn giản. 
                  Các tính năng nâng cao có gói trả phí với mức giá phù hợi.
                </p>
              </div>
              
              <div className="border-l-4 border-red-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Gói trả phí có những tính năng gì?</h3>
                <p className="text-gray-700">
                  Gói trả phí bao gồm: AI trò chuyện nâng cao, phân tích tâm trạng, báo cáo chi tiết cho gia đình, 
                  kết nối thiết bị IoT, và hỗ trợ ưu tiên.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6 text-gray-600">🆘 Hỗ trợ</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-gray-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Tôi gặp lỗi kỹ thuật, phải làm sao?</h3>
                <p className="text-gray-700">
                  Liên hệ ngay hotline 0374829059 hoặc email ngthuyn22@gmail.com. 
                  Chúng tôi hỗ trợ 8:00-18:00 hàng ngày và phản hồi trong 24h.
                </p>
              </div>
              
              <div className="border-l-4 border-gray-500 pl-6">
                <h3 className="text-lg font-medium mb-2">Có hướng dẫn sử dụng chi tiết không?</h3>
                <p className="text-gray-700">
                  Có, bạn có thể xem hướng dẫn chi tiết trong ứng dụng hoặc trên website. 
                  Chúng tôi cũng cung cấp video hướng dẫn và hỗ trợ trực tiếp.
                </p>
              </div>
            </div>
          </section>

          <div className="bg-gradient-to-r from-blue-50 to-green-50 p-8 rounded-lg mt-12">
            <h3 className="text-xl font-semibold mb-4">Chưa tìm thấy câu trả lời?</h3>
            <p className="mb-4">Đừng ngại liên hệ với chúng tôi:</p>
            <ul className="space-y-2">
              <li>📞 <strong>Hotline:</strong> 0374829059</li>
              <li>📧 <strong>Email:</strong> ngthuyn22@gmail.com</li>
              <li>⏰ <strong>Thời gian hỗ trợ:</strong> 8:00 - 18:00 (thứ 2 - chủ nhật)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQ;