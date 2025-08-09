import 'package:flutter/material.dart';

class MedicineInfoScreen extends StatefulWidget {
  // Trang này nhận dữ liệu thuốc (dưới dạng Map) được truyền từ trang camera.
  // 'name': Tên thuốc (String)
  // 'image_url': Đường dẫn đến ảnh sản phẩm (String)
  // 'description': Đoạn văn bản mô tả chi tiết về thuốc (String)
  final Map<String, dynamic> data;

  const MedicineInfoScreen({super.key, required this.data});

  @override
  State<MedicineInfoScreen> createState() => _MedicineInfoScreenState();
}

class _MedicineInfoScreenState extends State<MedicineInfoScreen> {

  bool _isListening = false;

  @override
  Widget build(BuildContext context) {

    final String name = widget.data['name'] ?? 'Không có tên';
    final String imageUrl = widget.data['image_url'] ?? 'assets/images/no_data.jpg';
    final String description = widget.data['description'] ?? 'Không có thông tin chi tiết.';
    final ThemeData theme = Theme.of(context);
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: theme.primaryColor),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 16),
                    Container(
                      height: 300,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        color: Colors.white,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.grey.withOpacity(0.2),
                            spreadRadius: 2,
                            blurRadius: 10,
                            offset: const Offset(0, 5),
                          ),
                        ],
                        image: DecorationImage(
                          fit: BoxFit.contain,
                            image: imageUrl.startsWith('http')
                                ? NetworkImage(imageUrl) as ImageProvider
                                : AssetImage(imageUrl) as ImageProvider,
                            onError: (exception, stackTrace) {
                              print('Lỗi tải ảnh mạng: $exception');
                            }
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Tên thuốc
                    Text(
                      name,
                      textAlign: TextAlign.center,
                      style: theme.textTheme.headlineMedium,
                    ),
                    const SizedBox(height: 16),
                    // Mô tả chi tiết
                    Text(
                      description,
                      textAlign: TextAlign.justify,
                      style: theme.textTheme.bodyLarge,
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Nút Micro
          _buildMicrophoneButton(),
        ],
      ),
    );
  }

  // Widget cho nút Micro
  Widget _buildMicrophoneButton() {
    final List<Color> gradientColors = _isListening
        ? [Colors.red.shade400, Colors.orange.shade400] // Màu khi đang "nghe"
        : [Colors.deepPurple.shade300, Colors.blue.shade400]; // Màu khi "tắt"

    return Padding(
      padding: const EdgeInsets.only(bottom: 32.0, top: 16.0),
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: (_isListening ? Colors.red : Colors.blue).withOpacity(0.15),
            ),
          ),
          // Nút bấm chính
          GestureDetector(
            onTap: () {
              // Cập nhật lại trạng thái khi người dùng nhấn vào
              setState(() {
                _isListening = !_isListening;
              });
              // TODO: Thêm logic bắt đầu/dừng nghe ở đây
            },
            child: Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                // Hiệu ứng gradient cho nút
                gradient: LinearGradient(
                  colors: gradientColors,
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: [
                  BoxShadow(
                    color: (_isListening ? Colors.red : Colors.deepPurple).withOpacity(0.4),
                    blurRadius: 10,
                    spreadRadius: 2,
                  )
                ],
              ),

              child: Icon(
                _isListening ? Icons.stop : Icons.mic,
                color: Colors.white,
                size: 35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
