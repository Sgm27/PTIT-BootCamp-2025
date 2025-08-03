import 'package:flutter/material.dart';
import '../../common_widgets/custom_nav_bar.dart';
import '../../features/notifications/notification_screen.dart';
import '../../features/profile/profile_screen.dart';

class GreetingScreen extends StatefulWidget {
  const GreetingScreen({super.key});

  @override
  State<GreetingScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<GreetingScreen> {
  // Biến state để xác định ai đang là vai trò chính (avatar to)
  // true: Người dùng là chính, false: Bác sĩ là chính
  bool _isUserMain = true;

  // Hàm để hoán đổi vai trò khi nhấn vào avatar nhỏ
  void _swapRoles() {
    setState(() {
      _isUserMain = !_isUserMain;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Xác định ảnh nào sẽ hiển thị ở vị trí chính và phụ dựa vào state
    final String mainAvatar = _isUserMain ? 'assets/images/user_avatar.png' : 'assets/images/doctor_avatar.png';
    final String secondaryAvatar = !_isUserMain ? 'assets/images/user_avatar.png' : 'assets/images/doctor_avatar.png';
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;
    final ThemeData theme = Theme.of(context);


    return Scaffold(
      extendBody: true, // Cho phép body hiển thị đằng sau BottomAppBar
      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        elevation: 0,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12.0),
            child: IconButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const NotificationScreen()),
                );
              },
              icon: Icon(Icons.notifications_outlined, color: theme.colorScheme.primary, size: 40),
            ),
          ),
        ],
      ),

      body: Stack(
        children: [
          // Avatar chính (to ở giữa)
          Positioned(
            top: 0, bottom: 0, left: 0, right: 0,
            child: Image.asset(
              mainAvatar,
              fit: BoxFit.cover,
            ),
          ),
          // Avatar phụ (nhỏ ở góc phải)
          Positioned(
            bottom: screenHeight * 0.15,
            right: screenWidth * 0.1,
            child: GestureDetector(
              onTap: _swapRoles, // Gọi hàm hoán đổi khi nhấn vào
              child: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 3),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey,
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    )
                  ],
                ),
                child: CircleAvatar(
                  radius: 30, // Kích thước avatar phụ
                  backgroundImage: AssetImage(secondaryAvatar),
                ),
              ),
            ),
          ),
        ],
      ),


      // Nút nổi ở giữa thanh điều hướng dưới
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

        bottomNavigationBar: CustomNavBar(
          activeIndex: 0, // Màn hình hiện tại là Home
          onHomeTap: () {
            // Đang ở Home rồi nên không cần làm gì
            print('Already on Home screen');
          },
          onProfileTap: () {
            // 👇 LOGIC ĐIỀU HƯỚNG ĐẾN TRANG PROFILE
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const ProfileScreen()),
            );
          },
          onCenterTap: () {
            // Xử lý nút giữa
          },
        ),
    );
  }

}