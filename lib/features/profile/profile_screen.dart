import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../common_widgets/custom_nav_bar.dart';
import '../../common_widgets/profile_menu_item.dart';
import '../../common_widgets/header_wave_painter.dart';
import '../history/medical_history_screen.dart';
import '../policy/privacy_policy_screen.dart';
import '../policy/help_and_support_screen.dart';
import 'edit_profile_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _notificationsEnabled = true;
  File? _imageFile; // file ảnh đã chọn

  // Hàm để mở thư viện và chọn ảnh
  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        _imageFile = File(pickedFile.path);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;

    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Phần Header
            _buildProfileHeader(context),

            Text('Lan Xinh', style: textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(
              'Web Designer | Morocco',
              style: textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
            ),

            const SizedBox(height: 20),
            // Phần thân với các thẻ cài đặt
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  _buildSettingsCard(
                    context,
                    children: [
                      ProfileMenuItem(
                        icon: Icons.edit_note,
                        iconSize: 30,
                        title: 'Chỉnh sửa hồ sơ',
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => const EditProfileScreen()),
                          );
                        },
                      ),
                      ProfileMenuItem(
                        icon: Icons.notifications_none,
                        iconSize: 30,
                        title: 'Thông báo',
                        onTap: () {},
                        trailing: Switch(
                          value: _notificationsEnabled,
                          onChanged: (value) {
                            setState(() {
                              _notificationsEnabled = value;
                            });
                          },
                          activeColor: theme.colorScheme.primary,
                          inactiveThumbColor: theme.colorScheme.primary.withOpacity(0.5),
                          inactiveTrackColor: theme.colorScheme.primary.withOpacity(0.3),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  _buildSettingsCard(
                    context,
                    children: [
                      ProfileMenuItem(
                        icon: Icons.receipt_long,
                        iconSize: 30,
                        title: 'Lịch sử tra thuốc',
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => const MedicalHistoryScreen()),
                          );
                        },
                      ),
                      ProfileMenuItem(
                        icon: Icons.color_lens_outlined,
                        iconSize: 30,
                        title: 'Chế độ',
                        onTap: () {},
                        trailing: Text(
                          'Sáng',
                          style: textTheme.bodyLarge?.copyWith(color: Colors.grey),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  _buildSettingsCard(
                    context,
                    children: [
                      ProfileMenuItem(
                        icon: Icons.help_outline,
                        title: 'Trợ giúp & Hỗ trợ',
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => const HelpAndSupportScreen()),
                          );
                        },
                      ),
                      ProfileMenuItem(
                        icon: Icons.lock_outline,
                        iconSize: 30,
                        title: 'Chính sách bảo mật',
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => const PrivacyPolicyScreen()),
                          );
                        },
                      ),
                      ProfileMenuItem(
                        icon: Icons.logout,
                        iconSize: 30,
                        title: 'Đăng xuất',
                        onTap: () {},
                        color: Colors.red,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),

      // Sử dụng lại BottomNavBar đã tạo
      bottomNavigationBar: CustomNavBar(
        activeIndex: 1,
        onHomeTap: () => Navigator.pop(context),
        onProfileTap: () {},
        onCenterTap: () {
          print('Center button tapped!');
        },
      ),
      floatingActionButton: SizedBox(
        width: 78,
        height: 78,
        child: FloatingActionButton(
          onPressed: () {},
          backgroundColor: theme.colorScheme.primary,
          elevation: 4.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(50.0),
          ),
          child: const Icon(Icons.qr_code_scanner, size: 48),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }

  // Helper widget để xây dựng thẻ cài đặt
  Widget _buildSettingsCard(BuildContext context, {required List<Widget> children}) {
    return Container(
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
      child: Column(
        children: children,
      ),
    );
  }

  // Hàm xây dựng header
  Widget _buildProfileHeader(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Container(
      height: 310,
      child: Stack(
        children: [
          ClipPath(
            clipper: HeaderWaveClipper(),
            child: Image.asset(
              'assets/images/header_wave_painter.jpg',
              width: double.infinity,
              height: 370,
              fit: BoxFit.cover,
            ),
          ),

          // Avatar
          Positioned(
            top: 180,
            left: 0,
            right: 0,
            child: Center(
              child: GestureDetector(
                onTap: _pickImage,
                child: CircleAvatar(
                  radius: 54,
                  backgroundColor: Colors.white,
                  child: CircleAvatar(
                    radius: 50,
                    // Hiển thị ảnh đã chọn, nếu không có thì hiển thị ảnh mặc định
                    backgroundImage: _imageFile != null
                        ? FileImage(_imageFile!) as ImageProvider
                        : const NetworkImage('https://i.pinimg.com/736x/74/25/c1/7425c135fb196ea7ced7e34f895ca6eb.jpg'),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

