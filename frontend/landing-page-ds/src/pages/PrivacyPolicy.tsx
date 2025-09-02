const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Chính sách bảo mật</h1>
        
        <div className="prose prose-lg max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Thu thập thông tin</h2>
            <p>VCareMind thu thập các thông tin cần thiết để cung cấp dịch vụ trợ lý ảo chăm sóc sức khỏe cho người cao tuổi:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Thông tin cá nhân cơ bản (họ tên, tuổi, số điện thoại)</li>
              <li>Thông tin sức khỏe (lịch uống thuốc, tình trạng bệnh lý)</li>
              <li>Dữ liệu âm thanh từ cuộc trò chuyện với trợ lý ảo</li>
              <li>Thông tin liên hệ của người thân/caregiver</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Sử dụng thông tin</h2>
            <p>Thông tin được sử dụng để:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Cung cấp dịch vụ trợ lý ảo cá nhân hóa</li>
              <li>Nhắc nhở uống thuốc và chăm sóc sức khỏe</li>
              <li>Kết nối với gia đình và caregiver</li>
              <li>Cải thiện chất lượng dịch vụ</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Bảo mật dữ liệu</h2>
            <p>VCareMind cam kết bảo vệ thông tin của bạn bằng:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Mã hóa end-to-end cho tất cả dữ liệu nhạy cảm</li>
              <li>Tuân thủ tiêu chuẩn bảo mật ISO 27001</li>
              <li>Lưu trữ dữ liệu trên hạ tầng AWS bảo mật cao</li>
              <li>Kiểm soát truy cập nghiêm ngặt</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Chia sẻ thông tin</h2>
            <p>Thông tin chỉ được chia sẻ với:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Caregiver được ủy quyền</li>
              <li>Các đối tác y tế khi có sự đồng ý</li>
              <li>Cơ quan pháp luật khi có yêu cầu hợp pháp</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Quyền của người dùng</h2>
            <p>Bạn có quyền:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Truy cập và chỉnh sửa thông tin cá nhân</li>
              <li>Yêu cầu xóa dữ liệu</li>
              <li>Rút lại sự đồng ý bất kỳ lúc nào</li>
              <li>Khiếu nại về việc sử dụng dữ liệu</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Liên hệ</h2>
            <p>Nếu có thắc mắc về chính sách bảo mật, vui lòng liên hệ:</p>
            <p>Email: ngthuyn22@gmail.com</p>
            <p>Điện thoại: 0374829059</p>
          </section>

          <p className="text-sm text-muted-foreground mt-8">
            Chính sách này có hiệu lực từ ngày 01/01/2024 và có thể được cập nhật định kỳ.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;