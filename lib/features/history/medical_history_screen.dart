import 'package:flutter/material.dart';
import '../../common_widgets/history_card.dart';

class MedicalHistoryScreen extends StatelessWidget {
  const MedicalHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final List<Map<String, String>> historyData = [
      {'title': 'This is a very long title that breaks in three lines', 'subtitle': 'Lorem ipsum dolor sit amet.'},
      {'title': 'Yesterday', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
      {'title': 'Wed, 7 Nov', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
      {'title': 'Thu, 8 Nov', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
      {'title': 'Fri, 9 Nov', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
      {'title': 'Sat, 10 Nov', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
      {'title': 'Sun, 11 Nov', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
      {'title': 'Mon, 12 Nov', 'subtitle': 'Lorem ipsum dolor sit amet, consectetur Lo...'},
    ];

    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Theme.of(context).primaryColor, size: 30),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            children: [
              _buildHeader(context),
              const SizedBox(height: 24),
              _buildUniformHistoryGrid(context, historyData),
            ],
          ),
        ),
      ),
    );
  }

  // Widget header
  Widget _buildHeader(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 30),
      decoration: BoxDecoration(
        color: theme.colorScheme.secondary,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'Lịch sử tra thuốc',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: Theme.of(context).primaryColor,
              fontWeight: FontWeight.bold,
            ),
          ),

          Image.asset(
            'assets/images/medical_history_icon.png',
            height: 110,
          ),
        ],
      ),
    );
  }

  // Widget lưới lịch sử
  Widget _buildUniformHistoryGrid(BuildContext context, List<Map<String, String>> data) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: data.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16.0,
        mainAxisSpacing: 16.0,
        childAspectRatio: 1.1,
      ),
      itemBuilder: (context, index) {
        final item = data[index];
        return HistoryCard(
          title: item['title']!,
          subtitle: item['subtitle']!,
        );
      },
    );
  }
}