import 'package:flutter/material.dart';
import 'signup_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isMobileTabActive = true;
  bool _rememberMe = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;

    return Scaffold(
      body: Container(
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
                  'Chào mừng trở lại',
                  style: textTheme.headlineMedium?.copyWith(
                    color: theme.primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 40),
                // Thẻ đăng nhập chính
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
                      if (_isMobileTabActive)
                        _buildMobileForm(context)
                      else
                        _buildEmailForm(context),
                      const SizedBox(height: 16),
                      _buildRememberMeRow(context),
                      const SizedBox(height: 24),
                      _buildDivider(context),
                      const SizedBox(height: 24),
                      _buildGoogleLoginButton(context),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                _buildSignUpRow(context),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

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
                  color: !_isMobileTabActive ? Colors.white : theme.primaryColor,
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

  // form đăng nhập bằng số điện thoại
  Widget _buildMobileForm(BuildContext context) {
    return Column(
      children: [
        TextFormField(
          decoration: _inputDecoration(context, 'Số điện thoại', Icons.phone_android),
          keyboardType: TextInputType.phone,
        ),
        const SizedBox(height: 16),
        TextFormField(
          decoration: _inputDecoration(context, 'Mã xác thực', Icons.shield_outlined).copyWith(
            suffixIcon: TextButton(
              onPressed: () {},
              child: Text(
                'Lấy mã',
                style: TextStyle(color: Theme.of(context).primaryColor.withOpacity(0.6), fontWeight: FontWeight.bold),
              ),
            ),
          ),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 24),
        _buildLoginButton(context),
      ],
    );
  }

  // form đăng nhập bằng email
  Widget _buildEmailForm(BuildContext context) {
    return Column(
      children: [
        TextFormField(
          decoration: _inputDecoration(context, 'Địa chỉ Email', Icons.email_outlined),
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 16),
        TextFormField(
          decoration: _inputDecoration(context, 'Mật khẩu', Icons.lock_outline),
          obscureText: true,
        ),
        const SizedBox(height: 24),
        _buildLoginButton(context),
      ],
    );
  }

  // nút Đăng nhập chính
  Widget _buildLoginButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme.of(context).primaryColor,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: Text(
          'Đăng nhập',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(color: Colors.white, fontSize:20),
        ),
      ),
    );
  }

  // "Ghi nhớ đăng nhập" và "Quên mật khẩu"
  Widget _buildRememberMeRow(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            SizedBox(
              width: 24,
              height: 24,
              child: Checkbox(
                value: _rememberMe,
                onChanged: (value) => setState(() => _rememberMe = value!),
                activeColor: Theme.of(context).primaryColor,
              ),
            ),
            const SizedBox(width: 8),
            const Text('Ghi nhớ tôi'),
          ],
        ),
        TextButton(
          onPressed: () {},
          child: Text(
            'Quên mật khẩu?',
            style: TextStyle(color: Theme.of(context).primaryColor.withOpacity(0.6)),
          ),
        ),
      ],
    );
  }

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

  // nút "Tiếp tục với Google"
  Widget _buildGoogleLoginButton(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: () {},
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(double.infinity, 50),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      icon: Image.asset('assets/images/google_logo.png', height: 30), // Cần có ảnh logo Google trong assets
      label: const Text(
        'Tiếp tục với Google',
        style: TextStyle(color: Colors.black87, fontWeight: FontWeight.normal, fontSize: 20),
      ),
    );
  }

  Widget _buildSignUpRow(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Đã chưa có tài khoản?',
          style: TextStyle(
            fontSize: 20,
          ),
        ),
        TextButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const SignUpScreen()),
            );
          },
          child: Text(
            'Đăng kí',
            style: TextStyle(
              color: Theme
                  .of(context)
                  .primaryColor,
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
          ),
        ),
      ],
    );
  }

  // InputDecoration cho các TextFormField
  InputDecoration _inputDecoration(BuildContext context, String hintText, IconData icon) {
    return InputDecoration(
      hintText: hintText,
      prefixIcon: Icon(icon, color: Theme.of(context).primaryColor.withOpacity(0.6)),
      filled: true,
      fillColor: Theme.of(context).scaffoldBackgroundColor,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12.0),
        borderSide: BorderSide.none,
      ),
    );
  }
}
