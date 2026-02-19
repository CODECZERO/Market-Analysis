# Landing Page Specification

## Design System

### Colors
```css
:root {
  --primary: #0EA5E9;           /* Electric Blue */
  --primary-hover: #0284C7;
  --secondary: #8B5CF6;         /* Violet */
  --background: #0F172A;        /* Dark Navy */
  --card: #1E293B;              /* Slate-800 */
  --card-border: rgba(255, 255, 255, 0.1);
  --text: #F1F5F9;
  --text-muted: #94A3B8;
  --gradient: linear-gradient(135deg, #0EA5E9, #8B5CF6);
}
```

### Typography
```css
font-family: 'Inter', sans-serif;
h1: 64px / 700 / -0.02em
h2: 48px / 700 / -0.01em
h3: 32px / 600
body: 18px / 400 / 1.7
```

### Spacing
- Base unit: 8px
- Section padding: 96px vertical
- Card padding: 32px
- Gap: 24px

---

## Section Breakdown

### 1. Hero Section

**Layout:** Full viewport height, centered content

**Elements:**
- Animated headline: "Protect Your Brand Before It's Too Late"
- Typewriter effect on subheadline
- Live dashboard preview (floating, animated)
- CTA: "Start Free Trial" (primary) + "Watch Demo" (ghost)
- Social proof: "Join 1,200+ brands monitoring their reputation"

**Effects:**
- Gradient background with animated particles
- Floating orbs (CSS animations)
- Dashboard preview with subtle hover tilt

---

### 2. Problem/Solution Section

**Layout:** 3-column grid

| Problem | Our Solution | Your Benefit |
|---------|--------------|--------------|
| "Negative reviews spread fast" | "Real-time monitoring across 10+ platforms" | "Catch issues before they go viral" |
| "Manual tracking wastes time" | "AI analyzes sentiment automatically" | "Save 20+ hours per week" |
| "Missing critical mentions" | "Smart alerts for crisis detection" | "Never miss a PR disaster" |

**Effects:**
- 3D tilt on hover (vanilla-tilt.js)
- Icon animations on scroll

---

### 3. Feature Showcase (Bento Grid)

**Layout:** 6 cards, asymmetric grid

```
┌─────────────┬─────────────────────┐
│   Card 1    │       Card 2        │
│ Multi-Source│   AI Analysis       │
├─────────────┼──────────┬──────────┤
│   Card 3    │  Card 4  │  Card 5  │
│   Alerts    │ Reports  │   API    │
├─────────────┴──────────┴──────────┤
│            Card 6                 │
│      Competitor Tracking          │
└───────────────────────────────────┘
```

**Card Contents:**
1. **Multi-Source Tracking** - Reddit, X, News, Reviews
2. **AI Sentiment Analysis** - Emotions, urgency, topics
3. **Smart Alerts** - Email, Slack, SMS
4. **Automated Reports** - PDF, weekly digest
5. **API Access** - Integrate everywhere
6. **Competitor Intel** - Side-by-side comparison

**Effects:**
- Glassmorphism cards
- 3D depth on hover
- Subtle gradient borders

---

### 4. How It Works (3 Steps)

**Layout:** Horizontal timeline

```
  ┌─────────┐         ┌─────────┐         ┌─────────┐
  │    1    │ ──────> │    2    │ ──────> │    3    │
  │ Connect │         │ Analyze │         │  Act    │
  └─────────┘         └─────────┘         └─────────┘
     API icons        Brain network       Dashboard
```

**Effects:**
- Animated connection lines (SVG)
- Step icons pulse on scroll
- Progress indicator

---

### 5. Pricing Section

**Layout:** 3 cards horizontal

| Starter | Professional | Enterprise |
|---------|--------------|------------|
| $49/mo | $149/mo | Custom |
| 1 brand | 3 brands | Unlimited |
| 5k mentions | 25k mentions | Unlimited |
| Email support | Priority support | Dedicated CSM |

**Effects:**
- 3D flip animation on hover
- "Most Popular" badge on Professional
- Gradient border on hover

---

### 6. Social Proof Section

**Elements:**
- 3 testimonial cards (carousel)
- Logo marquee (infinite scroll)
- Stats counter: "1M+ mentions tracked"

**Testimonial Format:**
```
"[Quote text]"
— Name, Title @ Company
[Avatar] [5 stars]
```

---

### 7. FAQ Section

**Questions:**
1. What data sources do you monitor?
2. How accurate is the sentiment analysis?
3. Can I track multiple brands?
4. How do alerts work?
5. Is there an API?
6. What about data privacy?
7. Can I cancel anytime?
8. Do you offer a free trial?

**Effects:**
- Accordion expand/collapse
- Smooth height animation
- Plus/minus icon rotation

---

### 8. CTA Section

**Layout:** Full-width, centered

**Copy:**
- Headline: "Start protecting your brand today"
- Subline: "14-day free trial. No credit card required."
- CTA button: "Get Started Free"

**Effects:**
- Gradient background
- Floating brand logos
- Subtle pulse on CTA button

---

### 9. Footer

**Sections:**
- Logo + tagline
- Product: Features, Pricing, API Docs
- Company: About, Blog, Careers
- Legal: Privacy, Terms, Security
- Social icons

---

## Mobile Responsiveness

**Breakpoints:**
- Desktop: 1280px+
- Tablet: 768px - 1279px
- Mobile: < 768px

**Mobile Adjustments:**
- Stack columns vertically
- Reduce heading sizes by 30%
- Hide dashboard preview
- Simplify bento grid to 2 columns
- Collapse FAQ by default
