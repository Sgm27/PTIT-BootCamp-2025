import 'package:flutter/material.dart';
import 'features/home/home_screen.dart';
import '/features/auth/login_screen.dart';
import '/features/auth/signup_screen.dart';
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VCareMind',
      theme: ThemeData(

        fontFamily: 'Roboto',
        textTheme: const TextTheme(
          headlineLarge: TextStyle(fontSize: 32.0, fontWeight: FontWeight.bold),
          headlineMedium: TextStyle(fontSize: 28.0, fontWeight: FontWeight.w600),

          titleLarge: TextStyle(fontSize: 22.0, fontWeight: FontWeight.w600),
          titleMedium: TextStyle(fontSize: 16.0, fontWeight: FontWeight.w500),

          bodyLarge: TextStyle(fontSize: 20.0),
          bodyMedium: TextStyle(fontSize: 16.0),
          bodySmall: TextStyle(fontSize: 14.0, color: Colors.grey),

          labelLarge: TextStyle(fontSize: 14.0, fontWeight: FontWeight.bold, letterSpacing: 0.5),
        ),

        scaffoldBackgroundColor: const Color(0xFFedf2ff),

        colorScheme: ColorScheme.light(
          primary: Color(0xFF342BA8),
          onPrimary: Colors.white,

          secondary: Color(0xFFDFE6FF),
          onSecondary: Color(0xFF2f2b84),

          tertiary: Color(0xFFa2b1ff),
          onTertiary: Colors.white,

          error: Colors.red,
          onError: Colors.white,

          brightness: Brightness.light,

          surface: Color(0xFF5d5ff7),
          surfaceTint: Color(0xFFF6F7F8),

        ),


        appBarTheme: const AppBarTheme(
          foregroundColor: Colors.white,
        ),

        useMaterial3: true,
      ),
      debugShowCheckedModeBanner: false,
      // home: const LoginScreen(),
      // home: const SignUpScreen(),
      // home: const GreetingScreen(),
        home: const GreetingScreen(),

    );
  }
}