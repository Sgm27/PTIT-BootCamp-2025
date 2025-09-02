const Partners = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-4">Đối tác & Hợp tác</h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            VCareMind tự hào được đồng hành cùng những tổ chức uy tín hàng đầu trong lĩnh vực 
            y tế, công nghệ và xã hội để mang đến giải pháp chăm sóc toàn diện cho người cao tuổi Việt Nam.
          </p>
        </div>

        {/* Healthcare Partners */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8 text-center">🏥 Đối tác Y tế</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏥</span>
                </div>
                <h3 className="text-xl font-semibold">Bệnh viện Lão khoa Trung ương</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Cung cấp cơ sở dữ liệu y tế chuyên ngành lão khoa</li>
                <li>• Tư vấn nội dung chăm sóc sức khỏe</li>
                <li>• Hỗ trợ nghiên cứu và phát triển tính năng</li>
                <li>• Đào tạo nhân viên y tế sử dụng công nghệ</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏥</span>
                </div>
                <h3 className="text-xl font-semibold">Bệnh viện 108</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Cung cấp câu hỏi-đáp về bệnh lý</li>
                <li>• Xây dựng knowledge base y tế</li>
                <li>• Tích hợp hệ thống bệnh án điện tử</li>
                <li>• Hỗ trợ kỹ thuật và tư vấn chuyên môn</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">💊</span>
                </div>
                <h3 className="text-xl font-semibold">DrugBank Việt Nam</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Cơ sở dữ liệu thuốc chính thống</li>
                <li>• Thông tin thuốc được cấp phép tại VN</li>
                <li>• Cập nhật thường xuyên danh mục thuốc</li>
                <li>• Hỗ trợ tính năng nhận diện thuốc</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Technology Partners */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8 text-center">💻 Đối tác Công nghệ</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">☁️</span>
                </div>
                <h3 className="text-xl font-semibold">Amazon Web Services</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Hạ tầng cloud computing bảo mật cao</li>
                <li>• Dịch vụ AI và machine learning</li>
                <li>• Lưu trữ và xử lý dữ liệu quy mô lớn</li>
                <li>• Hỗ trợ kỹ thuật và tư vấn giải pháp</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="text-xl font-semibold">Google AI</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Công nghệ Gemini AI cho trò chuyện</li>
                <li>• Nhận diện và tổng hợp giọng nói</li>
                <li>• Xử lý ngôn ngữ tự nhiên tiếng Việt</li>
                <li>• Phân tích cảm xúc và tâm trạng</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔐</span>
                </div>
                <h3 className="text-xl font-semibold">Cybersecurity Vietnam</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Kiểm định bảo mật ứng dụng</li>
                <li>• Tư vấn tiêu chuẩn ISO 27001</li>
                <li>• Giám sát và phân tích mối đe dọa</li>
                <li>• Đào tạo an ninh thông tin</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Government & NGO Partners */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8 text-center">🏛️ Đối tác Chính phủ & Tổ chức</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏛️</span>
                </div>
                <h3 className="text-xl font-semibold">Bộ Y tế</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Chính sách chăm sóc người cao tuổi</li>
                <li>• Hỗ trợ triển khai tại cơ sở y tế</li>
                <li>• Nghiên cứu và phát triển giải pháp</li>
                <li>• Đào tạo nhân lực y tế</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🌍</span>
                </div>
                <h3 className="text-xl font-semibold">UNFPA Việt Nam</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Hỗ trợ nghiên cứu già hóa dân số</li>
                <li>• Chương trình chăm sóc người cao tuổi</li>
                <li>• Chia sẻ kinh nghiệm quốc tế</li>
                <li>• Hỗ trợ tài chính và kỹ thuật</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">👥</span>
                </div>
                <h3 className="text-xl font-semibold">Hội Người cao tuổi VN</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Kết nối cộng đồng người cao tuổi</li>
                <li>• Phản hồi và góp ý sản phẩm</li>
                <li>• Hỗ trợ triển khai thực địa</li>
                <li>• Tổ chức sự kiện và workshop</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Academic Partners */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-8 text-center">🎓 Đối tác Học thuật</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏫</span>
                </div>
                <h3 className="text-xl font-semibold">Đại học Y Hà Nội</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Nghiên cứu khoa học về lão khoa</li>
                <li>• Đào tạo nhân lực chuyên ngành</li>
                <li>• Thử nghiệm lâm sàng</li>
                <li>• Xuất bản nghiên cứu quốc tế</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔬</span>
                </div>
                <h3 className="text-xl font-semibold">Viện Y học Ứng dụng VN</h3>
              </div>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Nghiên cứu sức khỏe tinh thần NCT</li>
                <li>• Phát triển nội dung can thiệp</li>
                <li>• Đánh giá hiệu quả điều trị</li>
                <li>• Hướng dẫn thực hành lâm sàng</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Partnership Opportunities */}
        <section className="bg-gradient-to-r from-primary/10 to-primary-accent/10 p-8 rounded-lg">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-4">🤝 Cơ hội hợp tác</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              VCareMind luôn tìm kiếm những đối tác có cùng tầm nhìn về việc cải thiện 
              chất lượng cuộc sống của người cao tuổi thông qua công nghệ.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">🏥</span>
              </div>
              <h3 className="font-semibold mb-2">Bệnh viện</h3>
              <p className="text-sm text-gray-600">Tích hợp hệ thống, đào tạo nhân viên</p>
            </div>

            <div className="text-center p-4">
              <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">💼</span>
              </div>
              <h3 className="font-semibold mb-2">Doanh nghiệp</h3>
              <p className="text-sm text-gray-600">CSR, chăm sóc nhân viên, đầu tư</p>
            </div>

            <div className="text-center p-4">
              <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">🎓</span>
              </div>
              <h3 className="font-semibold mb-2">Trường học</h3>
              <p className="text-sm text-gray-600">Nghiên cứu, thực tập, phát triển</p>
            </div>

            <div className="text-center p-4">
              <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">🌍</span>
              </div>
              <h3 className="font-semibold mb-2">Tổ chức</h3>
              <p className="text-sm text-gray-600">NGO, quỹ từ thiện, hội đoàn</p>
            </div>
          </div>

          <div className="text-center mt-8">
            <p className="mb-4 text-gray-600">Quan tâm đến việc hợp tác với VCareMind?</p>
            <a 
              href="mailto:ngthuyn22@gmail.com?subject=Đề xuất hợp tác với VCareMind"
              className="inline-block bg-primary text-white px-8 py-3 rounded-lg hover:bg-primary/90 transition-colors font-medium"
            >
              Liên hệ hợp tác
            </a>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Partners;