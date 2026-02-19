import {
    Navbar,
    HeroSection,
    FeaturesSection,
    HowItWorksSection,
    DemoSection,
    CTASection,
    Footer,
} from "@/components/landing";
import { PageSEO } from "@/components/seo";

export default function LandingPage() {
    return (
        <div className="bg-slate-900 min-h-screen">
            <PageSEO.Home />
            <Navbar />
            <main>
                <HeroSection />
                <FeaturesSection />
                <HowItWorksSection />
                <DemoSection />
                <CTASection />
            </main>
            <Footer />
        </div>
    );
}
