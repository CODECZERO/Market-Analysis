import { Helmet } from "react-helmet-async";

interface SEOHeadProps {
    title?: string;
    description?: string;
    keywords?: string[];
    image?: string;
    url?: string;
    type?: "website" | "article";
    author?: string;
    publishedTime?: string;
    noindex?: boolean;
}

const DEFAULT_TITLE = "Avichal - AI-Powered Brand Reputation Monitoring";
const DEFAULT_DESCRIPTION = "Monitor your brand reputation across Reddit, Twitter, News & more. AI-powered sentiment analysis, crisis detection, and real-time alerts. Protect your brand today.";
const DEFAULT_KEYWORDS = [
    "brand monitoring",
    "reputation management",
    "sentiment analysis",
    "crisis detection",
    "social listening",
    "brand tracker",
    "media monitoring",
    "brand protection",
];
const DEFAULT_IMAGE = "/og-image.png";
const SITE_URL = "https://brandtracker.io";

export function SEOHead({
    title,
    description = DEFAULT_DESCRIPTION,
    keywords = DEFAULT_KEYWORDS,
    image = DEFAULT_IMAGE,
    url = SITE_URL,
    type = "website",
    author,
    publishedTime,
    noindex = false,
}: SEOHeadProps) {
    const fullTitle = title ? `${title} | Avichal` : DEFAULT_TITLE;
    const fullImage = image.startsWith("http") ? image : `${SITE_URL}${image}`;

    return (
        <Helmet>
            {/* Primary Meta Tags */}
            <title>{fullTitle}</title>
            <meta name="title" content={fullTitle} />
            <meta name="description" content={description} />
            <meta name="keywords" content={keywords.join(", ")} />
            {noindex && <meta name="robots" content="noindex, nofollow" />}

            {/* Open Graph / Facebook */}
            <meta property="og:type" content={type} />
            <meta property="og:url" content={url} />
            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={description} />
            <meta property="og:image" content={fullImage} />
            <meta property="og:site_name" content="Avichal" />

            {/* Twitter */}
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:url" content={url} />
            <meta name="twitter:title" content={fullTitle} />
            <meta name="twitter:description" content={description} />
            <meta name="twitter:image" content={fullImage} />

            {/* Article specific (for blog posts) */}
            {author && <meta property="article:author" content={author} />}
            {publishedTime && <meta property="article:published_time" content={publishedTime} />}

            {/* Additional SEO */}
            <link rel="canonical" href={url} />
            <meta name="theme-color" content="#2563eb" />
        </Helmet>
    );
}

// Pre-configured SEO for common pages
export const PageSEO = {
    Home: () => (
        <SEOHead
            description="AI-powered brand reputation monitoring. Track mentions across Reddit, Twitter, News & more. Real-time alerts and crisis detection."
            keywords={[...DEFAULT_KEYWORDS, "homepage", "brand management"]}
        />
    ),
    Pricing: () => (
        <SEOHead
            title="Pricing"
            description="Simple, transparent pricing for brand monitoring. Start free, scale as you grow. Plans from $49/month."
            keywords={["pricing", "plans", "brand monitoring cost", ...DEFAULT_KEYWORDS]}
        />
    ),
    Features: () => (
        <SEOHead
            title="Features"
            description="Explore Avichal features: AI sentiment analysis, crisis detection, multi-platform monitoring, Slack/Discord alerts, and more."
            keywords={["features", "sentiment analysis", "crisis detection", ...DEFAULT_KEYWORDS]}
        />
    ),
    Login: () => (
        <SEOHead
            title="Login"
            description="Sign in to your Avichal dashboard to monitor your brand reputation."
            noindex
        />
    ),
    Signup: () => (
        <SEOHead
            title="Sign Up - Start Free Trial"
            description="Create your Avichal account. 14-day free trial, no credit card required."
            keywords={["sign up", "register", "free trial", ...DEFAULT_KEYWORDS]}
        />
    ),
    Dashboard: () => (
        <SEOHead
            title="Dashboard"
            description="Your brand monitoring dashboard."
            noindex
        />
    ),
};
