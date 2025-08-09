import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/custom_colors.dart';

class AddLovedOneScreen extends StatefulWidget {
  const AddLovedOneScreen({super.key});

  @override
  State<AddLovedOneScreen> createState() => _AddLovedOneScreenState();
}

class _AddLovedOneScreenState extends State<AddLovedOneScreen> {
  final PageController _pageController = PageController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();

  @override
  void dispose() {
    _pageController.dispose();
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  // chuyển đến trang nhập OTP
  void _goToOtpPage() {
    print('Gửi OTP đến số: ${_phoneController.text}');

    _pageController.animateToPage(
      1,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  // xác thực OTP và hoàn tất
  void _confirmOtp() {
    print('Xác thực OTP: ${_otpController.text}');

    Navigator.of(context).pop();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Kết nối thành công!')),
    );
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
      ),
      body: PageView(
        controller: _pageController,
        physics: const NeverScrollableScrollPhysics(),
        children: [
          _buildPhoneInputStep(),
          _buildOtpInputStep(),
        ],
      ),
    );
  }

  /// GIAO DIỆN BƯỚC 1: NHẬP SỐ ĐIỆN THOẠI
  Widget _buildPhoneInputStep() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Kết nối với người thân',
            style: GoogleFonts.poppins(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.font),
          ),
          const SizedBox(height: 12),
          Text(
            'Nhập số điện thoại của người thân để gửi lời mời kết nối. Một mã xác nhận sẽ được gửi đến họ để xin phép truy cập.',
            style: GoogleFonts.poppins(fontSize: 16, color: AppColors.fontSecondary),
          ),
          const SizedBox(height: 40),
          _buildTextFieldSection(
            controller: _phoneController,
            label: 'Số điện thoại',
            hint: '09xxxxxxxx',
            keyboardType: TextInputType.phone,
          ),
          const Spacer(),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _goToOtpPage,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              ),
              child: Text('Gửi mã xác nhận', style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  /// GIAO DIỆN BƯỚC 2: NHẬP MÃ OTP
  Widget _buildOtpInputStep() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Xác nhận OTP',
            style: GoogleFonts.poppins(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.font),
          ),
          const SizedBox(height: 12),
          Text(
            'Chúng tôi đã gửi một mã gồm 6 chữ số đến số điện thoại ${_phoneController.text}.',
            style: GoogleFonts.poppins(fontSize: 16, color: AppColors.fontSecondary),
          ),
          const SizedBox(height: 40),
          _buildTextFieldSection(
            controller: _otpController,
            label: 'Mã xác nhận',
            hint: '------',
            keyboardType: TextInputType.number,
            isOtp: true,
          ),
          const SizedBox(height: 20),
          Align(
            alignment: Alignment.center,
            child: TextButton(
              onPressed: () { },
              child: Text('Gửi lại mã', style: GoogleFonts.poppins(color: AppColors.primary, fontWeight: FontWeight.w600)),
            ),
          ),
          const Spacer(),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _confirmOtp,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              ),
              child: Text('Xác nhận', style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  // xây dựng các ô nhập liệu
  Widget _buildTextFieldSection({
    required TextEditingController controller,
    required String label,
    required String hint,
    TextInputType keyboardType = TextInputType.text,
    bool isOtp = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.poppins(color: AppColors.font, fontWeight: FontWeight.w600, fontSize: 18),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.grey.shade200, width: 1),
          ),
          child: TextField(
            controller: controller,
            keyboardType: keyboardType,
            textAlign: isOtp ? TextAlign.center : TextAlign.start,
            style: GoogleFonts.poppins(
              color: AppColors.font,
              fontSize: isOtp ? 24 : 18,
              fontWeight: isOtp ? FontWeight.bold : FontWeight.w500,
              letterSpacing: isOtp ? 8.0 : 0.0,
            ),
            decoration: InputDecoration.collapsed(
              hintText: hint,
              hintStyle: GoogleFonts.poppins(color: AppColors.fontSecondary.withOpacity(0.5)),
            ),
          ),
        ),
      ],
    );
  }
}