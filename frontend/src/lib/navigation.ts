import { LayoutDashboard, LineChart, MessageSquareText, PlusCircle, DollarSign, Thermometer, Target, Users, FileText, Settings, Bell } from "lucide-react";

export const appNavItems = [
  {
    label: "Brands",
    to: "/brands",
    icon: LayoutDashboard,
  },
  {
    label: "Create Brand",
    to: "/brands/create",
    icon: PlusCircle,
  },
  // V4.0 Advanced Features
  {
    label: "Money Mode",
    to: "/money-mode",
    icon: DollarSign,
  },
  {
    label: "Crisis Monitor",
    to: "/crisis",
    icon: Thermometer,
  },
  {
    label: "Market Gap",
    to: "/market-gap",
    icon: Target,
  },
  // Team & Settings (shown at bottom of sidebar)
  {
    label: "Team",
    to: "/team",
    icon: Users,
  },
];

export const brandNavItems = (brandId: string) => [
  {
    label: "Dashboard",
    to: `/brands/${brandId}/dashboard`,
    icon: LayoutDashboard,
  },
  {
    label: "Live Mentions",
    to: `/brands/${brandId}/live`,
    icon: MessageSquareText,
  },
  {
    label: "Analytics",
    to: `/brands/${brandId}/analytics`,
    icon: LineChart,
  },
  {
    label: "Web Insights",
    to: `/brands/${brandId}/web-insights`,
    icon: Target,
  },
  {
    label: "Competitors",
    to: `/brands/${brandId}/competitors`,
    icon: Users,
  },
  {
    label: "Reports",
    to: `/brands/${brandId}/reports`,
    icon: FileText,
  },
];
