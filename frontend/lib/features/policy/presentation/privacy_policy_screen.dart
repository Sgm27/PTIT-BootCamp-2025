import 'package:flutter/material.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        elevation: 0,
        title: Text('Chính sách bảo mật',
          style: theme.textTheme.headlineMedium?.copyWith(
            color: theme.primaryColor,
          ),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, size: 30),
          color: theme.primaryColor,
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24.0, 24.0, 24.0, 24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildPolicySection(
                  context,
                  title: '1. Các loại dữ liệu chúng tôi thu thập',
                  content:
                  'Để mang lại trải nghiệm tốt nhất và hỗ trợ sức khỏe tinh thần cho người cao tuổi, chúng tôi có thể thu thập các thông tin sau:\n\n'
                      '• Thông tin cá nhân cơ bản: Họ tên, tuổi, giới tính.\n'
                      '• Dữ liệu sức khỏe: Các ghi chú về tâm trạng, chất lượng giấc ngủ, và các hoạt động hàng ngày mà bạn chia sẻ.\n'
                      '• Dữ liệu tương tác: Nội dung các cuộc trò chuyện của bạn với trợ lý ảo để giúp trợ lý hiểu và hỗ trợ bạn tốt hơn.',
                ),
                const SizedBox(height: 24),
                _buildPolicySection(
                  context,
                  title: '2. Cách chúng tôi sử dụng dữ liệu của bạn',
                  content:
                  'Dữ liệu của bạn được sử dụng với mục đích cao nhất là chăm sóc cho bạn:\n\n'
                      '• Cá nhân hóa trải nghiệm: Trợ lý ảo sẽ dựa vào thông tin bạn cung cấp để đưa ra những lời khuyên, bài tập tinh thần, và những câu chuyện phù hợp.\n'
                      '• Theo dõi sức khỏe: Giúp bạn và người thân (nếu được cho phép) theo dõi sự thay đổi về tâm trạng và sức khỏe tinh thần theo thời gian.\n'
                      '• Cải thiện dịch vụ: Chúng tôi sử dụng dữ liệu đã được ẩn danh để cải tiến sự thông minh và khả năng hỗ trợ của trợ lý ảo.',
                ),
                const SizedBox(height: 24),
                _buildPolicySection(
                  context,
                  title: '3. Việc chia sẻ và bảo mật thông tin',
                  content:
                  'Sự riêng tư của bạn là ưu tiên hàng đầu của chúng tôi:\n\n'
                      '• Cam kết bảo mật: Chúng tôi cam kết không bán hoặc chia sẻ thông tin cá nhân của bạn cho bất kỳ bên thứ ba nào vì mục đích quảng cáo.\n'
                      '• Chia sẻ với sự cho phép: Thông tin của bạn chỉ được chia sẻ cho người thân hoặc bác sĩ khi có sự đồng ý rõ ràng từ bạn.\n'
                      '• An toàn dữ liệu: Mọi dữ liệu đều được mã hóa và lưu trữ trên các hệ thống an toàn để đảm bảo không bị truy cập trái phép.',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Widget helper để xây dựng mỗi phần chính sách cho gọn gàng
  Widget _buildPolicySection(BuildContext context, {required String title, required String content}) {
    final textTheme = Theme.of(context).textTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: textTheme.titleLarge?.copyWith(
            color: Theme.of(context).primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12.0),
        Text(
          content,
          style: textTheme.bodyLarge?.copyWith(
            color: Colors.black87,
            height: 1.5,
          ),
          textAlign: TextAlign.justify,
        ),
      ],
    );
  }
}
