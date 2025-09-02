import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  MessageCircle, 
  Pill, 
  Camera, 
  Users, 
  Heart, 
  BookOpen,
  Phone,
  Shield
} from "lucide-react";

const Features = () => {
  const features = [
    {
      icon: MessageCircle,
      title: "Trò chuyện & Đồng hành tinh thần",
      description: "Trợ lý ảo giọng nói thân thiện, hỏi thăm hằng ngày và ghi lại hồi ký quý giá của người cao tuổi.",
      gradient: "bg-gradient-healthcare"
    },
    {
      icon: Pill,
      title: "Nhắc nhở y tế thông minh",
      description: "Nhắc lịch uống thuốc, vận động, ăn uống bằng giọng nói gần gũi và dễ nghe.",
      gradient: "bg-gradient-primary"
    },
    {
      icon: Camera,
      title: "Quét & Quản lý thuốc",
      description: "Nhận diện tên thuốc, công dụng, liều lượng chỉ bằng cách chụp ảnh.",
      gradient: "bg-gradient-warm"
    },
    {
      icon: Users,
      title: "Kết nối với gia đình",
      description: "Con cháu theo dõi tình trạng sức khỏe và nhận thông báo từ xa một cách tiện lợi.",
      gradient: "bg-gradient-healthcare"
    },
    {
      icon: Heart,
      title: "Chăm sóc tinh thần",
      description: "Tập trung vào sức khỏe tinh thần, giúp người cao tuổi bớt cô đơn và có động lực sống.",
      gradient: "bg-gradient-primary"
    },
    {
      icon: BookOpen,
      title: "Hồi ký số tự động",
      description: "AI ghi nhớ và nhắc lại những câu chuyện quý giá, tạo thành hồi ký số để lưu giữ.",
      gradient: "bg-gradient-warm"
    },
    {
      icon: Phone,
      title: "Voice-first Design",
      description: "Tối ưu cho giọng nói, không phụ thuộc màn hình, phù hợp với người cao tuổi.",
      gradient: "bg-gradient-healthcare"
    },
    {
      icon: Shield,
      title: "Bảo mật & An toàn",
      description: "Dữ liệu được mã hóa, tuân thủ các tiêu chuẩn bảo mật quốc tế về thông tin y tế.",
      gradient: "bg-gradient-primary"
    }
  ];

  return (
    <section id="features" className="py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <Badge variant="outline" className="mb-4">
            Tính năng nổi bật
          </Badge>
          <h2 className="text-3xl md:text-5xl font-bold text-foreground mb-6">
            Công nghệ AI tiên tiến cho{" "}
            <span className="bg-gradient-healthcare bg-clip-text text-transparent">
              chăm sóc toàn diện
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            VCareMind kết hợp trí tuệ nhân tạo với tình người, mang đến giải pháp chăm sóc 
            sức khỏe tinh thần và thể chất cho người cao tuổi Việt Nam.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card 
                key={index} 
                className="group hover:shadow-healthcare transition-all duration-300 hover:-translate-y-1 border-border/50"
              >
                <CardHeader className="pb-4">
                  <div className={`w-12 h-12 ${feature.gradient} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-lg font-semibold text-foreground">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;