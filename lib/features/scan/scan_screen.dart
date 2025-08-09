import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'medicine_info_screen.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  CameraController? _controller;
  bool _isInitialized = false;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  // Khởi tạo camera
  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      final firstCamera = cameras.first;

      _controller = CameraController(
        firstCamera,
        ResolutionPreset.high,
        enableAudio: false,
      );

      await _controller!.initialize();

      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Lỗi khởi tạo camera: ${e.toString()}')),
        );
      }
    }
  }

  // Hàm thực hiện chụp ảnh và gửi đi xử lý
  Future<void> _takePictureAndAnalyze() async {
    if (!_isInitialized || _isProcessing) {
      return;
    }

    setState(() {
      _isProcessing = true;
    });

    try {
      // Chụp ảnh
      final XFile imageFile = await _controller!.takePicture();

      // GỬI ẢNH TỚI BACKEND VÀ NHẬN DẠNG (PHẦN GIẢ LẬP)
      // ====================================================================
      // TODO: Đây là nơi bạn sẽ gọi API thật để gửi `imageFile` đi.
      //
      await Future.delayed(const Duration(seconds: 2));
      final mockMedicineData = {
        'name': 'Paracetamol 500mg',
        'usage': 'Giảm đau, hạ sốt.',
        'dosage': 'Người lớn: 1-2 viên/lần, 3-4 lần/ngày.',
        'side_effects': 'Hiếm gặp, có thể gây phát ban hoặc dị ứng.',
      };
      // ====================================================================


      // 3. ĐIỀU HƯỚNG SANG TRANG THÔNG TIN THUỐC
      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => MedicineInfoScreen(data: mockMedicineData),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Lỗi khi chụp ảnh: ${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Nhận dạng thuốc',
            style: theme.textTheme.headlineMedium?.copyWith(color: Colors.white),
            textAlign: TextAlign.center,
        ),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        centerTitle: true,
        iconTheme: const IconThemeData(
          size: 30,
          color: Colors.white,
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 10.0),
          child: Column(
            children: [
              Text(
                'Đưa thuốc vào khung hình',
                style: theme.textTheme.bodyLarge?.copyWith(color: Colors.white),
                textAlign: TextAlign.center,
              ),
              // const Spacer(flex: 1),
              SizedBox(height: 130),
              _buildCameraPreview(),

              const Spacer(flex: 1),

              // Nút chụp ảnh, có trạng thái loading
              ElevatedButton.icon(
                onPressed: (_isInitialized && !_isProcessing) ? _takePictureAndAnalyze : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.primaryColor,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 56),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  disabledBackgroundColor: Colors.grey.shade700,
                ),
                icon: _isProcessing
                    ? Container(
                  width: 24,
                  height: 24,
                  padding: const EdgeInsets.all(2.0),
                  child: const CircularProgressIndicator(
                    color: Colors.white,
                    strokeWidth: 3,
                  ),
                )
                    : const Icon(Icons.camera_alt, size: 30),
                label: Text(
                  _isProcessing ? 'Đang xử lý...' : 'Chụp và nhận dạng',
                  style: theme.textTheme.labelLarge?.copyWith(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Widget hiển thị camera preview
  Widget _buildCameraPreview() {
    final previewSize = MediaQuery.of(context).size.width * 0.85;

    if (!_isInitialized || _controller == null) {
      // Hiển thị loading trong khi chờ camera
      return SizedBox(
        width: previewSize,
        height: previewSize,
        child: const Center(child: CircularProgressIndicator()),
      );
    }

    return SizedBox(
      width: previewSize,
      height: previewSize,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: CameraPreview(_controller!),
      ),
    );
  }
}
