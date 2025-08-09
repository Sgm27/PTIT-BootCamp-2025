import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class MedicalHistoryScreen extends StatelessWidget {
  const MedicalHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);

    final List<Map<String, String>> historyData = [
      {
        'title': 'Paracetamol 500mg',
        'subtitle': 'Giảm đau, hạ sốt thông thường.',
        // URL trực tiếp đến ảnh .jpg
        'imageUrl': 'https://www.vinmec.com/static/uploads/20230218_051500_983773_Paracetamol_500mg_max_1800x1800_jpg_5789437962.jpg',
      },
      {
        'title': 'Amoxicillin 250mg',
        'subtitle': 'Kháng sinh điều trị nhiễm khuẩn.',
        // URL trực tiếp đến ảnh .png
        'imageUrl': 'https://cdn.upharma.vn/unsafe/3840x0/filters:quality(90)/san-pham/5665.png',
      },
      {
        'title': 'Berberin 100mg',
        'subtitle': 'Hỗ trợ điều trị tiêu chảy, nhiễm khuẩn đường ruột.',
        // URL trực tiếp đến ảnh .jpg
        'imageUrl': 'https://medlatec.vn/media/22848/file/Thuoc-dau-bung-berberin-2.jpg',
      },
      {
        'title': 'Loratadine 10mg',
        'subtitle': 'Thuốc kháng histamine, trị dị ứng.',
        // URL trực tiếp đến ảnh .png
        'imageUrl': 'https://trungsoncare.com/images/detailed/11/1_b8jz-vk.png',
      },
    ];

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: theme.colorScheme.primary, size: 30),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context),
              const SizedBox(height: 32),
              _buildHistoryList(context, historyData),
            ],
          ),
        ),
      ),
    );
  }

  // Widget header
  Widget _buildHeader(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Lịch sử tra thuốc',
                  style: GoogleFonts.poppins(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                    fontSize: 24,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Xem lại các loại thuốc bạn đã tra cứu gần đây.',
                  style: GoogleFonts.poppins(
                    color: theme.colorScheme.primary.withOpacity(0.8),
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
          Image.asset(
            'assets/images/medical_history_icon.png',
            height: 100,
          ),
        ],
      ),
    );
  }

  // danh sách lịch sử dạng ListView
  Widget _buildHistoryList(BuildContext context, List<Map<String, String>> data) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: data.length,
      itemBuilder: (context, index) {
        final item = data[index];
        return _buildHistoryItem(
          context: context,
          title: item['title']!,
          subtitle: item['subtitle']!,
          imageUrl: item['imageUrl']!,
        );
      },
    );
  }

  // item thong tin thuoc
  Widget _buildHistoryItem({
    required BuildContext context,
    required String title,
    required String subtitle,
    required String imageUrl,
  }) {
    final ThemeData theme = Theme.of(context);
    return Card(
      elevation: 2,
      color: Colors.white,
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      shadowColor: Colors.grey.withOpacity(0.2),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            // Phần ảnh thuốc
            ClipRRect(
              borderRadius: BorderRadius.circular(12.0),
              child: Image.network(
                imageUrl,
                width: 150,
                height: 150,
                fit: BoxFit.contain,

                loadingBuilder: (context, child, progress) {
                  return progress == null ? child : const Center(child: CircularProgressIndicator());
                },
                errorBuilder: (context, error, stackTrace) {
                  return const Icon(Icons.error_outline, size: 40);
                },
              ),
            ),
            const SizedBox(width: 16),
            // Phần tên và mô tả thuốc
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.poppins(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                      color: theme.textTheme.bodyLarge?.color,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    subtitle,
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      color: theme.textTheme.bodyMedium?.color?.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}