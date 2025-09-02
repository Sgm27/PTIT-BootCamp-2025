const TermsOfService = () => {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Điều khoản sử dụng</h1>
        
        <div className="prose prose-lg max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Giới thiệu</h2>
            <p>
              Chào mừng bạn đến với VCareMind - ứng dụng trợ lý ảo chăm sóc sức khỏe tinh thần cho người cao tuổi. 
              Bằng việc sử dụng ứng dụng, bạn đồng ý tuân thủ các điều khoản sau đây.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Phạm vi dịch vụ</h2>
            <p>VCareMind cung cấp:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Trợ lý ảo giọng nói hỗ trợ tinh thần</li>
              <li>Nhắc nhở uống thuốc và chăm sóc sức khỏe</li>
              <li>Quét và nhận diện thông tin thuốc</li>
              <li>Kết nối với gia đình và caregiver</li>
              <li>Tính năng hồi ký bằng giọng nói</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Trách nhiệm người dùng</h2>
            <p>Người dùng cam kết:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Cung cấp thông tin chính xác và đầy đủ</li>
              <li>Sử dụng dịch vụ đúng mục đích</li>
              <li>Không lạm dụng hoặc sử dụng sai mục đích</li>
              <li>Bảo mật thông tin đăng nhập</li>
              <li>Tuân thủ pháp luật hiện hành</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Giới hạn trách nhiệm</h2>
            <p><strong>Quan trọng:</strong> VCareMind là công cụ hỗ trợ và KHÔNG thay thế:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Lời khuyên y tế chuyên nghiệp</li>
              <li>Chẩn đoán của bác sĩ</li>
              <li>Điều trị y khoa</li>
              <li>Dịch vụ cấp cứu y tế</li>
            </ul>
            <p className="text-red-600 font-medium">
              Trong trường hợp khẩn cấp, vui lòng liên hệ ngay với cơ sở y tế hoặc gọi 115.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Quyền sở hữu trí tuệ</h2>
            <p>
              Tất cả nội dung, công nghệ và tài sản trí tuệ của VCareMind được bảo vệ bởi luật sở hữu trí tuệ. 
              Người dùng không được sao chép, phân phối hoặc sử dụng trái phép.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Chính sách thanh toán</h2>
            <p>Đối với các gói dịch vụ trả phí:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Thanh toán được thực hiện qua các kênh an toàn</li>
              <li>Không hoàn tiền sau khi kích hoạt dịch vụ</li>
              <li>Gia hạn tự động trừ khi hủy trước thời hạn</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Chấm dứt dịch vụ</h2>
            <p>VCareMind có quyền tạm dừng hoặc chấm dứt dịch vụ nếu:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Người dùng vi phạm điều khoản</li>
              <li>Sử dụng dịch vụ cho mục đích bất hợp pháp</li>
              <li>Có hành vi gây tổn hại đến hệ thống</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Thay đổi điều khoản</h2>
            <p>
              VCareMind có quyền cập nhật điều khoản sử dụng. Người dùng sẽ được thông báo trước khi 
              các thay đổi có hiệu lực.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Liên hệ và hỗ trợ</h2>
            <p>Để được hỗ trợ, vui lòng liên hệ:</p>
            <p>Email: ngthuyn22@gmail.com</p>
            <p>Điện thoại: 0374829059</p>
            <p>Địa chỉ: Hà Nội, Việt Nam</p>
          </section>

          <p className="text-sm text-muted-foreground mt-8">
            Điều khoản này có hiệu lực từ ngày 01/01/2024.
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsOfService;