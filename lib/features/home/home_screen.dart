import 'package:flutter/material.dart';
import '../../core/common_widgets/custom_nav_bar.dart';
import '../history/chat_history_screen.dart';
import '../notifications/notification_screen.dart';
import '../profile/profile_screen.dart';
import '../scan/scan_screen.dart';

class GreetingScreen extends StatefulWidget {
  const GreetingScreen({super.key});

  @override
  State<GreetingScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<GreetingScreen> {
  bool _isListening = false;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      extendBody: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,

        // button lịch sử trò chuyện
        leading: Padding(
          padding: const EdgeInsets.only(left: 12.0),
          child: IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ChatHistoryScreen()),
              );
            },
            icon: Icon(Icons.history_rounded, color: theme.colorScheme.primary, size: 40),
          ),
        ),
        // end button lịch sử trò chuyên

        // button noti
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
      // end button noti

      // chatbot
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              'assets/images/doctor_avatar.png',
              fit: BoxFit.cover,
            ),
          ),
          Positioned(
            bottom: screenHeight * 0.15,
            right: screenWidth * 0.08,
            child: _buildMicrophoneButton(),
          ),
        ],
      ),
      //end chatbot

      // navbar
      floatingActionButton: SizedBox(
        width: 78,
        height: 78,
        child: FloatingActionButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const ScanScreen()),
            );
          },
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
        activeIndex: 0,
        onHomeTap: () {},
        onProfileTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const ProfileScreen()),
          );
        },
        onCenterTap: () {},
      ),
      //end navbar

    );
  }

  // button microphone
  Widget _buildMicrophoneButton() {
    final gradientColors = _isListening
        ? [Colors.red.shade400, Colors.orange.shade400]
        : [Colors.blue.shade300, Colors.purple.shade300];

    final shadowColor = _isListening ? Colors.red : Colors.purple;
    final icon = _isListening ? Icons.stop_rounded : Icons.mic_none_rounded;

    return GestureDetector(
      onTap: () {
        setState(() {
          _isListening = !_isListening;
        });
      },
      child: Container(
        width: 60,
        height: 60,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: LinearGradient(
            colors: gradientColors,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          boxShadow: [
            BoxShadow(
              color: shadowColor.withOpacity(0.5),
              blurRadius: 15,
              spreadRadius: 2,
            )
          ],
        ),
        child: Icon(icon, color: Colors.white, size: 30), 
      ),
    );
  }
  // end button microphone
}