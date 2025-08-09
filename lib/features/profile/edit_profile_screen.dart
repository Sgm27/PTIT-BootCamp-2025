import 'package:flutter/material.dart';
import '../../core/common_widgets/custom_text_field.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  late final TextEditingController _nameController;
  late final TextEditingController _nickNameController;
  late final TextEditingController _emailController;
  late final TextEditingController _phoneController;
  late final TextEditingController _addressController;

  @override
  void initState() {
    super.initState();
    // Khởi tạo giá trị ban đầu cho các ô nhập liệu
    _nameController = TextEditingController(text: 'Puerto Rico');
    _nickNameController = TextEditingController(text: 'puerto_rico');
    _emailController = TextEditingController(text: 'youremail@domain.com');
    _phoneController = TextEditingController(text: '123-456-7890');
    _addressController = TextEditingController(text: 'Hà Đông, Hà Nội');
  }

  @override
  void dispose() {
    // Hủy các controller để tránh rò rỉ bộ nhớ
    _nameController.dispose();
    _nickNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.scaffoldBackgroundColor,
        title: Text(
          'Chỉnh sửa hồ sơ',
          style: theme.textTheme.headlineMedium?.copyWith(
            color: theme.primaryColor,
          ),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: Icon(
            Icons.arrow_back,
            color: Theme.of(context).primaryColor,
            size: 30,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              children: [
                const SizedBox(height: 30),
                CustomTextField(
                  labelText: 'Họ và tên',
                  controller: _nameController,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  labelText: 'Biệt danh',
                  controller: _nickNameController,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  labelText: 'Email',
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  readOnly: true,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  labelText: 'Số điện thoại',
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  labelText: 'Địa chỉ',
                  controller: _addressController,
                ),
                const SizedBox(height: 60),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      // Logic lưu thông tin
                      print('Name: ${_nameController.text}');
                      print('Address: ${_addressController.text}');
                      Navigator.of(context).pop();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: theme.colorScheme.primary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      'Lưu',
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}