import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/custom_colors.dart';

ThemeData datePickerTheme(BuildContext context) {
  return Theme.of(context).copyWith(
    colorScheme: const ColorScheme.light(
      primary: AppColors.primary,
      onPrimary: Colors.white,
      onSurface: AppColors.font,
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: AppColors.primary,
      ),
    ),
    dialogBackgroundColor: Colors.white,
  );
}


class CreateScheduleScreen extends StatefulWidget {
  const CreateScheduleScreen({super.key});

  @override
  State<CreateScheduleScreen> createState() => _CreateScheduleScreenState();
}

class _CreateScheduleScreenState extends State<CreateScheduleScreen> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  DateTime? _selectedDate;
  TimeOfDay? _selectedTime;
  String? _selectedCategory;

  final List<Map<String, dynamic>> _categories = [
    {'label': 'Uống thuốc', 'icon': Icons.medical_services_outlined},
    {'label': 'Khám bệnh', 'icon': Icons.person_search_outlined},
    {'label': 'Tập thể dục', 'icon': Icons.directions_walk_outlined},
    {'label': 'Ăn uống', 'icon': Icons.restaurant_menu_outlined},
    {'label': 'Khác', 'icon': Icons.more_horiz},
  ];

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime(2101),
      builder: (context, child) {
        return Theme(
          data: datePickerTheme(context),
          child: child!,
        );
      },
    );
    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _selectTime(BuildContext context) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime ?? TimeOfDay.now(),
      builder: (context, child) {
        return Theme(
          data: datePickerTheme(context),
          child: child!,
        );
      },
    );
    if (picked != null && picked != _selectedTime) {
      setState(() => _selectedTime = picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.font),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text('Tạo lịch trình mới', style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: AppColors.font)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInputSection(
              child: TextField(
                controller: _titleController,
                style: GoogleFonts.poppins(color: AppColors.font, fontSize: 16, fontWeight: FontWeight.w500),
                decoration: InputDecoration.collapsed(
                  hintText: 'VD: Uống thuốc huyết áp',
                  hintStyle: GoogleFonts.poppins(color: AppColors.fontSecondary.withOpacity(0.7)),
                ),
              ),
              label: 'Tên lịch trình',
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildInputSection(
                    label: 'Ngày',
                    child: GestureDetector(
                      onTap: () => _selectDate(context),
                      child: Text(
                        _selectedDate == null ? 'Chọn ngày' : DateFormat('dd/MM/yyyy').format(_selectedDate!),
                        style: GoogleFonts.poppins(color: AppColors.font, fontSize: 16, fontWeight: FontWeight.w500),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildInputSection(
                    label: 'Thời gian',
                    child: GestureDetector(
                      onTap: () => _selectTime(context),
                      child: Text(
                        _selectedTime == null ? 'Chọn giờ' : _selectedTime!.format(context),
                        style: GoogleFonts.poppins(color: AppColors.font, fontSize: 16, fontWeight: FontWeight.w500),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInputSection(
              label: 'Ghi chú',
              child: TextField(
                controller: _descriptionController,
                maxLines: 4,
                style: GoogleFonts.poppins(color: AppColors.font, fontSize: 16),
                decoration: InputDecoration.collapsed(
                  hintText: 'Thêm mô tả chi tiết...',
                  hintStyle: GoogleFonts.poppins(color: AppColors.fontSecondary.withOpacity(0.7)),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text('Phân loại', style: GoogleFonts.poppins(color: AppColors.font, fontWeight: FontWeight.w600, fontSize: 18)),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12.0,
              runSpacing: 12.0,
              children: _categories.map((category) {
                final bool isSelected = _selectedCategory == category['label'];
                return ChoiceChip(
                  label: Text(category['label']),
                  labelStyle: GoogleFonts.poppins(color: isSelected ? Colors.white : AppColors.primary, fontWeight: FontWeight.w600),
                  avatar: Icon(category['icon'], color: isSelected ? Colors.white : AppColors.primary, size: 18),
                  selected: isSelected,
                  onSelected: (selected) => setState(() => _selectedCategory = selected ? category['label'] : null),
                  selectedColor: AppColors.primary,
                  backgroundColor: Theme.of(context).colorScheme.secondary,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                    side: BorderSide(color: isSelected ? AppColors.primary : Colors.transparent),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 80),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 5,
                  shadowColor: AppColors.primary.withOpacity(0.4),
                ),
                child: Text('Lưu Lịch Trình', style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildInputSection({required String label, required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.poppins(color: AppColors.font, fontWeight: FontWeight.w600, fontSize: 18),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.grey.shade200, width: 1),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: child,
        ),
      ],
    );
  }
}