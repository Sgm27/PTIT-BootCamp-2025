import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download as DownloadIcon, QrCode, Smartphone, Star } from "lucide-react";

const Download = () => {
  return (
    <section id="download" className="py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <Badge variant="outline" className="mb-4">
            Tải xuống miễn phí
          </Badge>
          <h2 className="text-3xl md:text-5xl font-bold text-foreground mb-6">
            Bắt đầu hành trình{" "}
            <span className="bg-gradient-healthcare bg-clip-text text-transparent">
              chăm sóc
            </span>{" "}
            ngay hôm nay
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            VCareMind hoàn toàn miễn phí. Tải xuống ngay để trải nghiệm trợ lý ảo 
            chăm sóc người cao tuổi tiên tiến nhất Việt Nam.
          </p>
        </div>
        
        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* QR Code Card */}
          <Card className="lg:col-span-1 hover:shadow-healthcare transition-all duration-300">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 bg-gradient-healthcare rounded-full flex items-center justify-center mx-auto mb-6">
                <QrCode className="w-8 h-8 text-white" />
              </div>
              
              <h3 className="text-xl font-bold text-foreground mb-4">
                Quét mã QR
              </h3>
              
              <div className="w-48 h-48 mx-auto mb-6 p-4 bg-white rounded-lg border">
                <img 
                  src="/asset/qr.png" 
                  alt="QR Code để tải VCareMind" 
                  className="w-full h-full object-contain"
                />
              </div>
              
              <p className="text-muted-foreground">
                Quét mã QR để tải xuống trực tiếp
              </p>
            </CardContent>
          </Card>
          
          {/* Download Options */}
          <Card className="lg:col-span-2 hover:shadow-healthcare transition-all duration-300">
            <CardContent className="p-8">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <Smartphone className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-foreground">
                    VCareMind App
                  </h3>
                  <p className="text-muted-foreground">
                    Phiên bản Android - Miễn phí hoàn toàn
                  </p>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button 
                    variant="healthcare" 
                    size="lg" 
                    className="flex-1"
                    onClick={() => window.open('https://drive.google.com/drive/folders/1DG_k7bWtF9gtS8foAMoj2_bcDowksTxT', '_blank')}
                  >
                    <DownloadIcon className="w-5 h-5" />
                    Tải xuống APK
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="lg"
                    onClick={() => window.open('https://drive.google.com/file/d/1v9giq6Zs4A-Q7WYelHXY1ZfGNq__d1oo/edit', '_blank')}
                  >
                    Xem video hướng dẫn
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-healthcare-green rounded-full" />
                    <span className="text-sm text-muted-foreground">Miễn phí 100%</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-healthcare-teal rounded-full" />
                    <span className="text-sm text-muted-foreground">Bảo mật cao</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                    <span className="text-sm text-muted-foreground">Hỗ trợ 24/7</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-center gap-1 pt-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                  <span className="ml-2 text-sm font-medium">5.0 từ người dùng thử nghiệm</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="text-center mt-16">
          <p className="text-muted-foreground mb-4">
            Cần hỗ trợ cài đặt? Liên hệ với chúng tôi
          </p>
          <Button variant="outline">
            Hỗ trợ kỹ thuật
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Download;