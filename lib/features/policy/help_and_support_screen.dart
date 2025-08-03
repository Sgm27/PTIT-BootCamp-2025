import 'package:flutter/material.dart';

class HelpAndSupportScreen extends StatelessWidget {
  const HelpAndSupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        title: Text('Trợ giúp & Hỗ trợ',
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
                _buildHelpSection(
                  context,
                  title: '1. Tính năng Quét Thuốc',
                  content:
                  'Khi có một loại thuốc mới, ông/bà chỉ cần dùng camera của điện thoại để quét vỏ hộp. Trợ lý ảo sẽ đọc to và hiển thị các thông tin quan trọng như:\n\n'
                      '• Tên thuốc và công dụng.\n'
                      '• Hướng dẫn sử dụng và liều lượng.\n'
                      '• Các lưu ý cần thiết.\n\n'
                      'Mọi thông tin về thuốc đã quét sẽ được lưu lại trong "Lịch sử tra thuốc" để ông/bà có thể xem lại bất cứ lúc nào.',
                ),
                const SizedBox(height: 24),
                _buildHelpSection(
                  context,
                  title: '2. Lời nhắc nhở bằng giọng nói',
                  content:
                  'Trợ lý ảo sẽ là người bạn đồng hành, luôn nhắc nhở ông/bà những việc quan trọng bằng một giọng nói ấm áp và thân thiện:\n\n'
                      '• Nhắc uống thuốc đúng giờ, đúng liều.\n'
                      '• Khuyến khích vận động nhẹ nhàng, tập thể dục tại nhà.\n'
                      '• Gửi các cảnh báo quan trọng về sức khỏe khi cần thiết.',
                ),
                const SizedBox(height: 24),
                _buildHelpSection(
                  context,
                  title: '3. Hồi kí - Nhật ký cuộc đời',
                  content:
                  'Mỗi cuộc trò chuyện, mỗi tâm sự của ông/bà với trợ lý ảo đều là một kỷ niệm quý giá. Tính năng "Hồi kí" sẽ giúp ông/bà:\n\n'
                      '• Tự động lưu lại những câu chuyện đã chia sẻ.\n'
                      '• Xem lại các cuộc trò chuyện như đọc một cuốn nhật ký.\n'
                      '• Giúp ông/bà nhìn lại hành trình cảm xúc và những khoảnh khắc đáng nhớ của mình.',
                ),
                const SizedBox(height: 24),
                _buildHelpSection(
                  context,
                  title: '4. Khi cần trợ giúp thêm',
                  content:
                  'Nếu có bất kỳ thắc mắc nào khác hoặc cần hỗ trợ kỹ thuật, xin đừng ngần ngại liên hệ với chúng tôi qua số điện thoại: 1800-1234 (miễn phí) hoặc email: hotro@trolyao.vn. Đội ngũ của chúng tôi luôn sẵn lòng lắng nghe.',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Widget helper để xây dựng mỗi phần trợ giúp
  Widget _buildHelpSection(BuildContext context, {required String title, required String content}) {
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
