import 'package:flutter/material.dart';

class CustomColors extends ThemeExtension<CustomColors> {
  const CustomColors({
    required this.background1,
    required this.background2,
  });

  final Color? background1;
  final Color? background2;

  @override
  CustomColors copyWith({Color? background1, Color? background2}) {
    return CustomColors(
      background1: background1 ?? this.background1,
      background2: background2 ?? this.background2,
    );
  }

  @override
  CustomColors lerp(ThemeExtension<CustomColors>? other, double t) {
    if (other is! CustomColors) {
      return this;
    }
    return CustomColors(
      background1: Color.lerp(background1, other.background1, t),
      background2: Color.lerp(background2, other.background2, t),
    );
  }
}