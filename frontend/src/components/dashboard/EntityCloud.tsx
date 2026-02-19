import { motion } from "framer-motion";
import { User, Building2, Package } from "lucide-react";

interface Entity {
    name: string;
    count: number;
}

interface EntityData {
    people: Entity[];
    companies: Entity[];
    products: Entity[];
}

interface EntityCloudProps {
    data: EntityData | null;
    isLoading: boolean;
}

export function EntityCloud({ data, isLoading }: EntityCloudProps) {
    if (isLoading) {
        return (
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex items-center justify-center min-h-[120px]">
                <div className="flex flex-col items-center gap-2">
                    <div className="w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                    <span className="text-zinc-500 text-xs">Loading entities...</span>
                </div>
            </div>
        );
    }

    // Helper to safely extract display name
    const getDisplayName = (entity: Entity): string => {
        if (typeof entity.name === 'string') return entity.name;
        if (typeof entity.name === 'object' && entity.name !== null) {
            return (entity.name as any).name || (entity.name as any).text || '';
        }
        return String(entity.name || '');
    };

    const processEntities = (entities: Entity[]) =>
        entities
            .map(e => ({ ...e, displayName: getDisplayName(e) }))
            .filter(e => e.displayName && e.displayName !== '[object Object]');

    const people = processEntities(data?.people || []);
    const companies = processEntities(data?.companies || []);
    const products = processEntities(data?.products || []);

    const isEmpty = people.length === 0 && companies.length === 0 && products.length === 0;

    if (isEmpty) {
        return (
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col items-center justify-center text-center min-h-[120px]">
                <div className="w-8 h-8 rounded-lg bg-zinc-800/50 flex items-center justify-center mb-2">
                    <Building2 className="w-4 h-4 text-zinc-600" />
                </div>
                <p className="text-sm text-zinc-400 font-medium">Entity Detection</p>
                <p className="text-xs text-zinc-600 mt-0.5">Entities will appear as they're detected</p>
            </div>
        );
    }

    // Build sections dynamically - only show sections with data
    const sections = [
        { title: "People", icon: <User className="w-3.5 h-3.5" />, entities: people, color: "purple" as const },
        { title: "Companies", icon: <Building2 className="w-3.5 h-3.5" />, entities: companies, color: "blue" as const },
        { title: "Products", icon: <Package className="w-3.5 h-3.5" />, entities: products, color: "emerald" as const },
    ].filter(section => section.entities.length > 0);

    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
                <Building2 className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-white">Entity Cloud</h3>
                <span className="ml-auto text-[10px] bg-zinc-800 text-zinc-500 px-2 py-0.5 rounded-full">
                    {people.length + companies.length + products.length} found
                </span>
            </div>
            <div className="flex flex-col gap-2.5">
                {sections.map(section => (
                    <EntitySection
                        key={section.title}
                        title={section.title}
                        icon={section.icon}
                        entities={section.entities}
                        color={section.color}
                    />
                ))}
            </div>
        </div>
    );
}


function EntitySection({
    title,
    icon,
    entities,
    color
}: {
    title: string;
    icon: React.ReactNode;
    entities: { displayName: string; count: number }[];
    color: "purple" | "blue" | "emerald";
}) {
    const colorClasses = {
        purple: {
            icon: "text-purple-400",
            tag: "bg-purple-500/10 text-purple-300 border-purple-500/20 hover:bg-purple-500/20",
            count: "text-purple-400"
        },
        blue: {
            icon: "text-blue-400",
            tag: "bg-blue-500/10 text-blue-300 border-blue-500/20 hover:bg-blue-500/20",
            count: "text-blue-400"
        },
        emerald: {
            icon: "text-emerald-400",
            tag: "bg-emerald-500/10 text-emerald-300 border-emerald-500/20 hover:bg-emerald-500/20",
            count: "text-emerald-400"
        }
    };

    const styles = colorClasses[color];

    return (
        <div className="flex items-start gap-2 flex-wrap">
            {/* Section Label */}
            <div className={`flex items-center gap-1.5 text-xs font-medium ${styles.icon}`}>
                {icon}
                <span>{title}</span>
            </div>

            {/* Entity Tags */}
            <div className="flex flex-wrap gap-2">
                {entities.slice(0, 10).map((entity, idx) => (
                    <motion.div
                        key={entity.displayName + idx}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.03 }}
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-medium transition-colors cursor-default ${styles.tag}`}
                    >
                        <span className="max-w-[100px] truncate">{entity.displayName}</span>
                        {entity.count > 1 && (
                            <span className={`text-[10px] font-semibold ${styles.count}`}>
                                ×{entity.count}
                            </span>
                        )}
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

