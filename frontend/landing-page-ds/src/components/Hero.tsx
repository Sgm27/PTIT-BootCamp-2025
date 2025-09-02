import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, Download, QrCode } from "lucide-react";
import heroImage from "@/assets/vcaremind-hero.jpg";

const Hero = () => {
  return (
    <section className="relative pt-20 pb-16 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-hero" />
      
      <div className="container relative mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <Badge variant="secondary" className="w-fit">
              🏆 95% mức độ hài lòng từ người dùng
            </Badge>
            
            <div className="space-y-6">
              <h1 className="text-4xl md:text-6xl font-bold text-foreground leading-tight">
                Trợ lý ảo{" "}
                <span className="bg-gradient-healthcare bg-clip-text text-transparent">
                  chăm sóc
                </span>{" "}
                người cao tuổi
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-lg">
                VCareMind - Giải pháp AI tiên tiến giúp người cao tuổi bớt cô đơn, 
                nhắc nhở uống thuốc và kết nối với gia đình. Sức khỏe tinh thần là ưu tiên hàng đầu.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                variant="hero" 
                size="lg"
                onClick={() => window.open('https://drive.google.com/drive/folders/1DG_k7bWtF9gtS8foAMoj2_bcDowksTxT', '_blank')}
              >
                <Download className="w-5 h-5" />
                Tải xuống miễn phí
              </Button>
              
              <Button 
                variant="outline" 
                size="lg"
                onClick={() => window.open('https://drive.google.com/file/d/1v9giq6Zs4A-Q7WYelHXY1ZfGNq__d1oo/edit', '_blank')}
              >
                <Play className="w-5 h-5" />
                Xem video giới thiệu
              </Button>
            </div>
            
            <div className="flex items-center gap-6 pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">50+</div>
                <div className="text-sm text-muted-foreground">Người dùng thử nghiệm</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">95%</div>
                <div className="text-sm text-muted-foreground">Mức độ hài lòng</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">24/7</div>
                <div className="text-sm text-muted-foreground">Hỗ trợ liên tục</div>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="relative">
              <img 
                src={heroImage} 
                alt="VCareMind - Trợ lý ảo chăm sóc người cao tuổi"
                className="w-full rounded-2xl shadow-healthcare animate-float"
              />
            </div>
            
            {/* Decorative elements */}
            <div className="absolute -top-4 -left-4 w-24 h-24 bg-gradient-healthcare rounded-full opacity-20 animate-pulse" />
            <div className="absolute -bottom-4 -right-4 w-32 h-32 bg-gradient-warm rounded-full opacity-20 animate-pulse delay-1000" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;