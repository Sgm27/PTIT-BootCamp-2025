import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Play, Download, QrCode, X } from "lucide-react";
import { useState } from "react";
import waitingAvatarVideo from "/asset/waiting_avatar.mp4";

const Hero = () => {
  const [isVideoOpen, setIsVideoOpen] = useState(false);

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
              
              <Dialog open={isVideoOpen} onOpenChange={setIsVideoOpen}>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="lg"
                  >
                    <Play className="w-5 h-5" />
                    Xem video giới thiệu
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl w-full p-0">
                  <div className="relative">
                    <button
                      onClick={() => setIsVideoOpen(false)}
                      className="absolute top-4 right-4 z-10 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <div className="aspect-video w-full">
                      <iframe
                        src="https://drive.google.com/file/d/1v9giq6Zs4A-Q7WYelHXY1ZfGNq__d1oo/preview"
                        className="w-full h-full rounded-lg"
                        allow="autoplay"
                        title="Video giới thiệu VCareMind"
                      />
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
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
          
          <div className="relative flex justify-center">
            <div className="relative w-fit">
              <video 
                src={waitingAvatarVideo} 
                autoPlay
                loop
                muted
                playsInline
                className="h-[500px] w-auto rounded-2xl shadow-healthcare object-cover"
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