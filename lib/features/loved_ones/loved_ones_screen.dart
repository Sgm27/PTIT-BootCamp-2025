import 'package:flutter/material.dart';
import '../../theme/custom_colors.dart';
import '../../core/common_widgets/pagination_dots.dart';
import 'widgets/loved_one_card.dart';
import 'widgets/notification_card_item.dart';
import 'schedule_screen.dart';
import 'add_loved_one_screen.dart';

class LovedOnesScreen extends StatefulWidget {
  const LovedOnesScreen({super.key});

  @override
  State<LovedOnesScreen> createState() => _LovedOnesScreenState();
}

class _LovedOnesScreenState extends State<LovedOnesScreen> {
  final PageController _pageController = PageController(viewportFraction: 0.85);
  int _currentPage = 0;

  final List<Map<String, dynamic>> _lovedOnesData = [
    {
      'name': 'Papa',
      'colors': [Colors.pink.shade300, Colors.red.shade300],
      'notifications': [
        {'icon': Icons.calendar_today_outlined, 'title': 'Nhắc nhở: Khám sức khỏe!', 'subtitle': 'Lịch hẹn khám sức khỏe vào thứ Bảy.', 'date': '06.08'},
        {'icon': Icons.local_pharmacy_outlined, 'title': 'Đã mua thuốc', 'subtitle': 'Thuốc huyết áp cho tháng này đã được mua.', 'date': '05.08'},
      ]
    },
    {
      'name': 'Mama',
      'colors': [Colors.orange.shade300, Colors.amber.shade400],
      'notifications': [
        {'icon': Icons.cake_outlined, 'title': 'Sắp đến sinh nhật Mama!', 'subtitle': 'Còn 2 tuần nữa là đến sinh nhật Mama.', 'date': '01.08'},
        {'icon': Icons.task_alt_outlined, 'title': 'Công việc nhà đã xong', 'subtitle': 'Đã dọn dẹp và đi chợ cho cả tuần.', 'date': 'Hôm qua'},
      ]
    },
  ];

  @override
  void initState() {
    super.initState();
    _pageController.addListener(() {
      if (_pageController.page == null) return;
      int next = _pageController.page!.round();
      if (_currentPage != next) {
        setState(() => _currentPage = next);
      }
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: theme.primaryColor, size: 30),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Kết nối yêu thương',
          style: theme.textTheme.headlineMedium?.copyWith(
            color: theme.colorScheme.primary,
          ),
        ),
      ),
      body: Column(
        children: [
          const SizedBox(height: 50),
          SizedBox(
            height: 200,
            child: PageView.builder(
              controller: _pageController,
              itemCount: _lovedOnesData.length,
              itemBuilder: (context, index) {
                final data = _lovedOnesData[index];
                final scale = index == _currentPage ? 1.0 : 0.85;
                return AnimatedScale(
                  duration: const Duration(milliseconds: 300),
                  scale: scale,
                  child: LovedOneCard(
                      name: data['name'],
                      colors: data['colors'],
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ScheduleScreen(lovedOneData: data),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 30),
          PaginationDots(itemCount: _lovedOnesData.length, currentIndex: _currentPage),
          const SizedBox(height: 24),
          Expanded(child: _buildNotificationsList()),
        ],
      ),
      floatingActionButton: _buildFAB(),
    );
  }

  Widget _buildFAB() {
    return FloatingActionButton(
      onPressed: () {
        // Điều hướng đến trang AddLovedOneScreen khi nhấn nút
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const AddLovedOneScreen()),
        );
      },
      backgroundColor: AppColors.primary,
      elevation: 4,
      child: const Icon(Icons.add, color: Colors.white),
    );
  }

  Widget _buildNotificationsList() {
    final notifications = _lovedOnesData[_currentPage]['notifications'];
    return Container(
      decoration: const BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.only(topLeft: Radius.circular(40.0), topRight: Radius.circular(40.0)),
          boxShadow: [BoxShadow(color: Color.fromARGB(25, 158, 158, 158), blurRadius: 20, spreadRadius: 5)]
      ),
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 350),
        transitionBuilder: (child, animation) => FadeTransition(opacity: animation, child: child),
        child: ListView.builder(
          key: ValueKey<int>(_currentPage),
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 80),
          itemCount: notifications.length,
          itemBuilder: (context, index) {
            final notif = notifications[index];
            return NotificationCardItem(
              icon: notif['icon'],
              title: notif['title'],
              subtitle: notif['subtitle'],
              date: notif['date'],
            );
          },
        ),
      ),
    );
  }
}