import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/custom_colors.dart';

class ChatHistoryScreen extends StatefulWidget {
  const ChatHistoryScreen({super.key});

  @override
  State<ChatHistoryScreen> createState() => _ChatHistoryScreenState();
}

class _ChatHistoryScreenState extends State<ChatHistoryScreen> {
  final List<Map<String, String>> _chatHistory = [
    {
      'name': 'Trò chuyện ngày 07/08/2025',
      'lastMessage': 'Chào buổi sáng, hôm nay ông cảm thấy thế nào ạ?',
      'time': '08:15 AM',
    },
    {
      'name': 'Trò chuyện ngày 06/08/2025',
      'lastMessage': 'Đã đến giờ uống thuốc huyết áp rồi ạ.',
      'time': 'Hôm qua',
    },
    {
      'name': 'Trò chuyện ngày 05/08/2025',
      'lastMessage': 'Thời tiết hôm nay khá đẹp, ông có muốn đi dạo không?',
      'time': '05/08',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.font),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Lịch sử trò chuyện',
          style: GoogleFonts.poppins(
            color: AppColors.font,
            fontWeight: FontWeight.w600,
            fontSize: 20,
          ),
        ),
      ),
      body: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 10.0),
        itemCount: _chatHistory.length,
        itemBuilder: (context, index) {
          final chat = _chatHistory[index];
          return _buildChatItem(
            name: chat['name']!,
            lastMessage: chat['lastMessage']!,
            time: chat['time']!,
          );
        },
        separatorBuilder: (context, index) => const Divider(
          height: 1,
          thickness: 1,
          indent: 16,
          endIndent: 16,
          color: Colors.black12,
        ),
      ),
    );
  }

  // Widget cho một item trong danh sách chat
  Widget _buildChatItem({
    required String name,
    required String lastMessage,
    required String time,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 16.0),
      title: Text(
        name,
        style: GoogleFonts.poppins(
          fontWeight: FontWeight.bold,
          fontSize: 16,
          color: AppColors.font,
        ),
      ),
      subtitle: Text(
        lastMessage,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: GoogleFonts.poppins(
          fontSize: 14,
          color: AppColors.fontSecondary,
        ),
      ),
      trailing: Text(
        time,
        style: GoogleFonts.poppins(
          fontSize: 12,
          color: AppColors.fontSecondary,
        ),
      ),
      onTap: () {
        print('Tapped on chat with $name');
      },
    );
  }
}