import 'package:flutter/material.dart';

class CustomNavBar extends StatelessWidget {
  // Biến để xác định tab nào đang active
  // 0: Home, 1: Profile
  final int activeIndex;

  // Hàm callback khi nhấn vào các icon
  final VoidCallback onHomeTap;
  final VoidCallback onProfileTap;
  final VoidCallback onCenterTap;

  const CustomNavBar({
    super.key,
    required this.activeIndex,
    required this.onHomeTap,
    required this.onProfileTap,
    required this.onCenterTap,
  });

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);

    return BottomAppBar(
      shape: const CircularNotchedRectangle(),
      notchMargin: 8.0,
      color: theme.colorScheme.secondary,
      child: Container(
        height: 60.0,
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            // Nút Home
            IconButton(
              icon: Icon(
                Icons.home_rounded,
                size: 50,
                // Thay đổi màu sắc dựa trên activeIndex
                color: activeIndex == 0
                    ? theme.colorScheme.primary
                    : theme.colorScheme.tertiary,
              ),
              onPressed: onHomeTap,
            ),
            // Nút Profile
            IconButton(
              icon: Icon(
                Icons.person_outline,
                size: 50,
                // Thay đổi màu sắc dựa trên activeIndex
                color: activeIndex == 1
                    ? theme.colorScheme.primary
                    : theme.colorScheme.tertiary,
              ),
              onPressed: onProfileTap,
            ),
          ],
        ),
      ),
    );
  }
}