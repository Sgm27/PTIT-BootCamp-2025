import 'package:flutter/material.dart';

class ProfileMenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget? trailing;
  final VoidCallback onTap;
  final Color? color; // Tùy chọn màu cho icon và chữ (dùng cho Logout)
  final double? iconSize;

  const ProfileMenuItem({
    super.key,
    required this.icon,
    required this.title,
    required this.onTap,
    this.trailing,
    this.color,
    this.iconSize,
  });

  @override
  Widget build(BuildContext context) {
    final titleStyle = Theme.of(context).textTheme.bodyLarge?.copyWith(
      fontWeight: FontWeight.w500,
    );

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 20.0),
        child: Row(
          children: [
            Icon(icon, size: iconSize, color: color ?? Theme.of(context).colorScheme.primary),
            const SizedBox(width: 16),
            Expanded(child: Text(title, style: Theme.of(context).textTheme.bodyLarge)),
            if (trailing != null) trailing!,
          ],
        ),
      ),
    );
  }
}