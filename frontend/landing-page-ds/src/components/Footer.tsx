import { Brain, Mail, Phone, MapPin } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-healthcare rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold">VCareMind</span>
            </div>
            <p className="text-background/70 leading-relaxed">
              Trợ lý ảo AI tiên tiến chăm sóc sức khỏe tinh thần người cao tuổi, 
              kết nối yêu thương giữa các thế hệ.
            </p>
          </div>
          
          {/* Product */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Sản phẩm</h3>
            <ul className="space-y-3 text-background/70">
              <li><a href="#features" className="hover:text-background transition-colors">Tính năng</a></li>
              <li><a href="#download" className="hover:text-background transition-colors">Tải xuống</a></li>
              <li><a href="/user-guide" className="hover:text-background transition-colors">Hướng dẫn sử dụng</a></li>
              <li><a href="/faq" className="hover:text-background transition-colors">FAQ</a></li>
            </ul>
          </div>
          
          {/* Company */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Công ty</h3>
            <ul className="space-y-3 text-background/70">
              <li><a href="#about" className="hover:text-background transition-colors">Giới thiệu</a></li>
              <li><a href="/research" className="hover:text-background transition-colors">Nghiên cứu</a></li>
              <li><a href="/partners" className="hover:text-background transition-colors">Đối tác</a></li>
              <li><a href="/news" className="hover:text-background transition-colors">Tin tức</a></li>
            </ul>
          </div>
          
          {/* Contact */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Liên hệ</h3>
            <div className="space-y-3 text-background/70">
              <div className="flex items-center gap-3">
                <Mail className="w-4 h-4" />
                <span>ngthuyn22@gmail.com</span>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="w-4 h-4" />
                <span>0374829059</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-4 h-4" />
                <span>Hà Nội, Việt Nam</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="border-t border-background/20 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-background/70 text-sm">
              © 2024 VCareMind. Bảo lưu mọi quyền.
            </div>
            
            <div className="flex items-center gap-6 text-sm text-background/70">
              <a href="/privacy-policy" className="hover:text-background transition-colors">
                Chính sách bảo mật
              </a>
              <a href="/terms-of-service" className="hover:text-background transition-colors">
                Điều khoản sử dụng
              </a>
              <a href="mailto:ngthuyn22@gmail.com" className="hover:text-background transition-colors">
                Liên hệ
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;