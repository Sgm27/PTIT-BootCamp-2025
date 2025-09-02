import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";

const Header = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border/50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img 
            src="/asset/logo.png" 
            alt="VCareMind Logo" 
            className="w-10 h-10 rounded-lg object-contain"
          />
          <span className="text-xl font-bold text-foreground">VCareMind</span>
        </div>
        
        <nav className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-foreground hover:text-primary transition-colors">
            Tính năng
          </a>
          <a href="#about" className="text-foreground hover:text-primary transition-colors">
            Giới thiệu
          </a>
          <a href="#download" className="text-foreground hover:text-primary transition-colors">
            Tải xuống
          </a>
          <Button variant="healthcare" size="sm" asChild>
            <a href="#download">Dùng thử ngay</a>
          </Button>
        </nav>
        
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
};

export default Header;