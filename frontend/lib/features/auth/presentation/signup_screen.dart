import 'package:flutter/material.dart';
import 'login_screen.dart';
class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  // Biến để quản lý trạng thái của tab (true: Mobile, false: Email)
  bool _isMobileTabActive = true;
  // Biến để quản lý hiển thị mật khẩu
  bool _isPasswordObscured = true;
  bool _isConfirmPasswordObscured = true;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;

    return Scaffold(
      body: Container(
        // Background gradient
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFE9E9FF), Colors.white],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 100),
                Text(
                  'Tạo tài khoản',
                  style: textTheme.headlineMedium?.copyWith(
                    color: theme.primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 40),
                // Thẻ đăng ký chính
                Container(
                  padding: const EdgeInsets.all(24.0),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20.0),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withOpacity(0.1),
                        blurRadius: 10,
                        offset: const Offset(0, 5),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      _buildTabSelector(context),
                      const SizedBox(height: 24),
                      // Hiển thị form tương ứng với tab được chọn
                      if (_isMobileTabActive)
                        _buildMobileForm(context)
                      else
                        _buildEmailForm(context),
                      const SizedBox(height: 24),
                      _buildDivider(context),
                      const SizedBox(height: 24),
                      _buildGoogleLoginButton(context),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                _buildLoginRow(context),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Widget cho bộ chọn Tab (Số điện thoại / Email)
  Widget _buildTabSelector(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: BorderRadius.circular(12.0),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextButton(
              onPressed: () => setState(() => _isMobileTabActive = true),
              style: TextButton.styleFrom(
                backgroundColor: _isMobileTabActive ? theme.primaryColor : Colors.transparent,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12.0)),
                padding: const EdgeInsets.symmetric(vertical: 14.0),
              ),
              child: Text(
                'Số điện thoại',
                style: TextStyle(
                  color: _isMobileTabActive ? Colors.white : theme.primaryColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 20.0,
                ),
              ),
            ),
          ),
          Expanded(
            child: TextButton(
              onPressed: () => setState(() => _isMobileTabActive = false),
              style: TextButton.styleFrom(
                backgroundColor: !_isMobileTabActive ? theme.primaryColor : Colors.transparent,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12.0)),
                padding: const EdgeInsets.symmetric(vertical: 14.0),
              ),
              child: Text(
                'Email',
                style: TextStyle(
                  color: _isMobileTabActive ? theme.primaryColor : Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 20.0,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Widget cho form đăng ký bằng số điện thoại
  Widget _buildMobileForm(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Họ và tên',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _inputDecoration(context, 'Nhập họ và tên của bạn'),
          keyboardType: TextInputType.name,
        ),
        const SizedBox(height: 8),
        Text(
          'Số điện thoại',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _inputDecoration(context, 'Nhập số điện thoại'),
          keyboardType: TextInputType.phone,
        ),
        const SizedBox(height: 8),
        Text(
          'Mật khẩu',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _passwordInputDecoration(context, 'Nhập mật khẩu', _isPasswordObscured, () {
            setState(() => _isPasswordObscured = !_isPasswordObscured);
          }),
          obscureText: _isPasswordObscured,
        ),
        const SizedBox(height: 8),
        Text(
          'Xác nhận mật khẩu',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _passwordInputDecoration(context, 'Nhập lại mật khẩu', _isConfirmPasswordObscured, () {
            setState(() => _isConfirmPasswordObscured = !_isConfirmPasswordObscured);
          }),
          obscureText: _isConfirmPasswordObscured,
        ),
        const SizedBox(height: 24),
        _buildSignUpButton(context),
      ],
    );
  }

  // Widget cho form đăng ký bằng email
  Widget _buildEmailForm(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Họ và tên',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _inputDecoration(context, 'Nhập họ và tên của bạn'),
          keyboardType: TextInputType.name,
        ),
        const SizedBox(height: 8),
        Text(
          'Email',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _inputDecoration(context, 'Nhập email của bạn'),
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 8),
        Text(
          'Mật khẩu',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _passwordInputDecoration(context, 'Nhập mật khẩu', _isPasswordObscured, () {
            setState(() => _isPasswordObscured = !_isPasswordObscured);
          }),
          obscureText: _isPasswordObscured,
        ),
        const SizedBox(height: 8),
        Text(
          'Xác nhận mật khẩu',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          decoration: _passwordInputDecoration(context, 'Nhập lại mật khẩu', _isConfirmPasswordObscured, () {
            setState(() => _isConfirmPasswordObscured = !_isConfirmPasswordObscured);
          }),
          obscureText: _isConfirmPasswordObscured,
        ),
        const SizedBox(height: 24),
        _buildSignUpButton(context),
      ],
    );
  }

  // Widget cho nút Đăng ký chính
  Widget _buildSignUpButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
          // Logic đăng ký ở đây
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme.of(context).primaryColor,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: Text(
          'Đăng ký',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(color: Colors.white, fontSize: 20),
        ),
      ),
    );
  }

  // Widget cho dải phân cách "Hoặc"
  Widget _buildDivider(BuildContext context) {
    return const Row(
      children: [
        Expanded(child: Divider()),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 8.0),
          child: Text('Hoặc', style: TextStyle(color: Colors.grey)),
        ),
        Expanded(child: Divider()),
      ],
    );
  }

  // Widget cho nút "Tiếp tục với Google"
  Widget _buildGoogleLoginButton(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: () {},
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(double.infinity, 50),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      icon: Image.asset('assets/images/google_logo.png', height: 24),
      label: Text(
        ' Tiếp tục với Google',
        style: Theme.of(context).textTheme.bodyLarge,
      ),
    );
  }

  // Widget cho dòng "Đã có tài khoản? Đăng nhập"
  Widget _buildLoginRow(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Đã có tài khoản?',
          style: TextStyle(
            fontSize: 20,
          ),
        ),
        TextButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const LoginScreen()),
            );
          },
          child: Text(
            'Đăng nhập',
            style: TextStyle(
              color: Theme.of(context).primaryColor,
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
          ),
        ),
      ],
    );
  }

  // Helper để tạo InputDecoration cho các TextFormField thông thường
  InputDecoration _inputDecoration(BuildContext context, String hintText) {
    return InputDecoration(
      hintText: hintText,
      hintStyle: TextStyle(color: Theme.of(context).primaryColor.withOpacity(0.6)),
      filled: true,
      fillColor: Theme.of(context).scaffoldBackgroundColor,
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12.0),
        borderSide: BorderSide.none,
      ),
    );
  }

  // Helper để tạo InputDecoration cho các ô mật khẩu
  InputDecoration _passwordInputDecoration(BuildContext context, String hintText, bool isObscured, VoidCallback onPressed) {
    return _inputDecoration(context, hintText).copyWith(
      suffixIcon: IconButton(
        icon: Icon(
          isObscured ? Icons.visibility_off_outlined : Icons.visibility_outlined,
          color: Colors.grey,
        ),
        onPressed: onPressed,
      ),
    );
  }
}
