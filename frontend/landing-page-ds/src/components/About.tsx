import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import elderlyUsingApp from "@/assets/elderly-using-app.jpg";
import familyConnection from "@/assets/family-connection.jpg";

const About = () => {
  const stats = [
    { number: "16.1 triệu", label: "Người cao tuổi dự kiến năm 2025" },
    { number: "17-20 năm", label: "Thời gian chuyển sang dân số già" },
    { number: "90%", label: "Người cao tuổi muốn được chăm sóc tại nhà" },
    { number: "34.4%", label: "Người cao tuổi có dấu hiệu trầm cảm" }
  ];

  return (
    <section id="about" className="py-20">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-16 items-center mb-20">
          <div className="space-y-8">
            <div>
              <Badge variant="outline" className="mb-4">
                Bối cảnh xã hội
              </Badge>
              <h2 className="text-3xl md:text-5xl font-bold text-foreground mb-6">
                Việt Nam đang{" "}
                <span className="bg-gradient-healthcare bg-clip-text text-transparent">
                  già hóa dân số
                </span>{" "}
                với tốc độ nhanh nhất châu Á
              </h2>
            </div>
            
            <p className="text-lg text-muted-foreground leading-relaxed">
              Theo dự báo của Liên Hợp Quốc, Việt Nam sẽ chính thức bước vào giai đoạn 
              "xã hội già" vào năm 2036. Quá trình này diễn ra nhanh hơn nhiều so với 
              các quốc gia phát triển, đặt ra những thách thức lớn về chăm sóc sức khỏe 
              tinh thần của người cao tuổi.
            </p>
            
            <div className="grid grid-cols-2 gap-6">
              {stats.map((stat, index) => (
                <div key={index} className="text-center p-4 rounded-lg bg-muted/50">
                  <div className="text-2xl md:text-3xl font-bold text-primary mb-2">
                    {stat.number}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="relative">
            <img 
              src={elderlyUsingApp} 
              alt="Người cao tuổi sử dụng VCareMind"
              className="w-full rounded-2xl shadow-healthcare"
            />
          </div>
        </div>
        
        <Card className="bg-gradient-hero border-0 shadow-elegant">
          <CardContent className="p-8 md:p-12">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <img 
                  src={familyConnection} 
                  alt="Gia đình kết nối qua công nghệ"
                  className="w-full rounded-xl"
                />
              </div>
              
              <div className="space-y-6">
                <Badge variant="secondary" className="w-fit">
                  Giải pháp của VCareMind
                </Badge>
                
                <h3 className="text-2xl md:text-4xl font-bold text-foreground">
                  Cầu nối yêu thương giữa các thế hệ
                </h3>
                
                <p className="text-lg text-muted-foreground leading-relaxed">
                  VCareMind không chỉ là một ứng dụng công nghệ, mà còn là người bạn đồng hành 
                  tinh thần, giúp người cao tuổi cảm thấy được quan tâm và bớt cô đơn. 
                  Đồng thời, ứng dụng tạo ra cầu nối số hóa giữa con cháu và người thân, 
                  giúp gia đình yên tâm hơn trong việc chăm sóc từ xa.
                </p>
                
                <div className="grid grid-cols-3 gap-4 pt-4">
                  <div className="text-center">
                    <div className="text-xl font-bold text-primary">Mental-first</div>
                    <div className="text-xs text-muted-foreground">Tập trung tinh thần</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-primary">Voice-first</div>
                    <div className="text-xs text-muted-foreground">Ưu tiên giọng nói</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-primary">Family-first</div>
                    <div className="text-xs text-muted-foreground">Kết nối gia đình</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default About;