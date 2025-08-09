import 'package:flutter/material.dart';
import '../../core/common_widgets/notification_card.dart';

class NotificationScreen extends StatelessWidget {
  const NotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {

    final ThemeData theme = Theme.of(context);

    return Scaffold(

      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(
            Icons.arrow_back,
            color: Theme.of(context).primaryColor,
            size: 35,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Thông báo',
          style: theme.textTheme.headlineMedium?.copyWith(
            color: theme.primaryColor,
          ),
        ),
        centerTitle: true,
      ),

      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
        children: const [
          NotificationCard(
            title: 'Notification Title',
            subtitle: 'Lorem ipsum dolor sit amet, consectetur Lorem ipsum dolor',
            dotColor: Color(0xFF6A5AE0),
          ),
          NotificationCard(
            title: 'Notification Title',
            subtitle: 'Lorem ipsum dolor sit amet, consectetur Lorem ipsum dolor',
            dotColor: Colors.orangeAccent,
          ),
          NotificationCard(
            title: 'Notification Title',
            subtitle: 'Lorem ipsum dolor sit amet, consectetur Lorem ipsum dolor',
            dotColor: Colors.cyan,
          ),
          NotificationCard(
            title: 'Notification Title',
            subtitle: 'Lorem ipsum dolor sit amet, consectetur Lorem ipsum dolor',
            dotColor: Colors.orangeAccent,
          ),
        ],
      ),
    );
  }
}