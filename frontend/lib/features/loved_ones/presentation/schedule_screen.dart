import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/custom_colors.dart';
import 'create_schedule_screen.dart';

class ScheduleScreen extends StatefulWidget {
  final Map<String, dynamic> lovedOneData;

  const ScheduleScreen({super.key, required this.lovedOneData});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  final List<Map<String, dynamic>> _schedules = [
    {
      'date': 'Hôm nay, 07 tháng 8',
      'tasks': [
        {'type': 'medicine', 'title': 'Uống thuốc huyết áp', 'time': '08:00 AM', 'status': 'completed'},
        {'type': 'appointment', 'title': 'Tái khám bác sĩ Tim mạch', 'time': '10:30 AM', 'status': 'pending'},
        {'type': 'exercise', 'title': 'Đi bộ 30 phút', 'time': '04:00 PM', 'status': 'pending'},
      ]
    },
    {
      'date': 'Hôm qua, 06 tháng 8',
      'tasks': [
        {'type': 'medicine', 'title': 'Uống thuốc huyết áp', 'time': '08:00 AM', 'status': 'completed'},
        {'type': 'medicine', 'title': 'Uống vitamin D', 'time': '12:00 PM', 'status': 'completed'},
        {'type': 'exercise', 'title': 'Đi bộ 30 phút', 'time': '04:00 PM', 'status': 'completed'},
      ]
    },
  ];

  IconData _getIconForTaskType(String type) {
    switch (type) {
      case 'medicine':
        return Icons.medical_services_outlined;
      case 'appointment':
        return Icons.person_search_outlined;
      case 'exercise':
        return Icons.directions_walk_outlined;
      default:
        return Icons.task_alt_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    final String name = widget.lovedOneData['name'] ?? '...';
    final List<Color> colors = widget.lovedOneData['colors'] ?? [Colors.grey, Colors.blueGrey];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: _buildAppBar(),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 32),
            _buildHeaderCard(name, colors),
            const SizedBox(height: 32),
            Text(
              "Lịch trình",
              style: GoogleFonts.poppins(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppColors.font,
              ),
            ),
            const SizedBox(height: 16),

            _buildScheduleList(),
          ],
        ),
      ),
    );
  }

  AppBar _buildAppBar() {
    final ThemeData theme = Theme.of(context);
    return AppBar(
      backgroundColor: AppColors.background,
      elevation: 0,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back, color: AppColors.primary),
        onPressed: () => Navigator.of(context).pop(),
      ),
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 16.0),
          child: ActionChip(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CreateScheduleScreen()),
              );
            },
            backgroundColor: theme.colorScheme.primary,
            avatar: const Icon(Icons.add, color: Colors.white, size: 18),
            label: Text(
              'Thêm',
              style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 18),
            ),

            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(15.0),
              side: BorderSide(
                color: Colors.white.withOpacity(0.8),
                width: 1.5,
              ),
            ),
          ),
        ),
      ],
    );
  }

  // Thẻ thông tin của người thân
  Widget _buildHeaderCard(String name, List<Color> colors) {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
          gradient: LinearGradient(colors: colors, begin: Alignment.topLeft, end: Alignment.bottomRight),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [BoxShadow(color: colors[0].withOpacity(0.4), blurRadius: 20, offset: const Offset(0, 10))]
      ),
      child: Align(
        alignment: Alignment.bottomLeft,
        child: Text(
          name,
          style: GoogleFonts.poppins(color: Colors.white, fontSize: 32, fontWeight: FontWeight.w700),
        ),
      ),
    );
  }

  // Danh sách các ngày và lịch trình tương ứng
  Widget _buildScheduleList() {
    return ListView.builder(
      itemCount: _schedules.length,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemBuilder: (context, index) {
        final daySchedule = _schedules[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                daySchedule['date'],
                style: GoogleFonts.poppins(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.fontSecondary,
                ),
              ),
              const SizedBox(height: 12),
              ... (daySchedule['tasks'] as List).map((task) {
                return _buildScheduleItem(task);
              }).toList(),
            ],
          ),
        );
      },
    );
  }

  // Giao diện cho một mục lịch trình
  Widget _buildScheduleItem(Map<String, dynamic> task) {
    final bool isCompleted = task['status'] == 'completed';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(_getIconForTaskType(task['type']), color: AppColors.primary, size: 28),
          const SizedBox(width: 24),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  task['title'],
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.font),
                ),
                const SizedBox(height: 4),
                Text(
                  task['time'],
                  style: GoogleFonts.poppins(fontSize: 14, color: AppColors.fontSecondary),
                ),
              ],
            ),
          ),

          IconButton(
            icon: Icon(
              isCompleted ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
              color: isCompleted ? Colors.green : Colors.grey.shade400,
              size: 28,
            ),
            onPressed: () {
              setState(() {
                if (isCompleted) {
                  task['status'] = 'pending';
                } else {
                  task['status'] = 'completed';
                }
              });
            },
          ),
        ],
      ),
    );
  }
}