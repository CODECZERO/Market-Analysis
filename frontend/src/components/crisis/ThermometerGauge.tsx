/**
 * Thermometer Gauge Component
 * 
 * Canvas-based animated risk score gauge
 */

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Shield } from "lucide-react";
import type { CrisisMetrics } from "./CrisisTypes";



interface ThermometerGaugeProps {
    metrics: CrisisMetrics;
}

export function ThermometerGauge({ metrics }: ThermometerGaugeProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [displayScore, setDisplayScore] = useState(0);

    useEffect(() => {
        const duration = 800;
        const start = displayScore;
        const end = metrics.riskScore;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            setDisplayScore(start + (end - start) * eased);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [metrics.riskScore]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const width = rect.width;
        const height = rect.height;
        const centerX = width / 2;
        const centerY = height - 30;
        const radius = Math.min(width, height) * 0.75;

        ctx.clearRect(0, 0, width, height);

        // Background Arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
        ctx.lineWidth = 12;
        ctx.strokeStyle = "#27272a";
        ctx.lineCap = "round";
        ctx.stroke();

        // Gradient for active arc
        const gradient = ctx.createLinearGradient(0, 0, width, 0);
        gradient.addColorStop(0, "#22c55e");
        gradient.addColorStop(0.5, "#eab308");
        gradient.addColorStop(1, "#ef4444");

        // Active Arc
        const angle = Math.PI + (displayScore / 100) * Math.PI;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, angle);
        ctx.lineWidth = 12;
        ctx.lineCap = "round";
        ctx.strokeStyle = gradient;

        ctx.shadowBlur = 15;
        ctx.shadowColor = displayScore > 60 ? "#ef4444" : displayScore > 30 ? "#eab308" : "#22c55e";
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Needle
        const needleAngle = Math.PI + (displayScore / 100) * Math.PI;
        const needleLength = radius - 10;
        const needleX = centerX + Math.cos(needleAngle) * needleLength;
        const needleY = centerY + Math.sin(needleAngle) * needleLength;

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(needleX, needleY);
        ctx.lineWidth = 4;
        ctx.lineCap = "round";
        ctx.strokeStyle = "#ffffff";
        ctx.stroke();

        // Needle Pivot
        ctx.beginPath();
        ctx.arc(centerX, centerY, 6, 0, 2 * Math.PI);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
    }, [displayScore]);

    const severityConfig = {
        normal: { color: "text-green-500", label: "Stable State" },
        warning: { color: "text-amber-500", label: "Elevated Risk" },
        critical: { color: "text-red-500", label: "Critical Threat" },
    };

    const config = severityConfig[metrics.severity];

    return (
        <div className="rounded-xl bg-zinc-900/30 backdrop-blur-sm border border-zinc-800/50 p-4 flex flex-col h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 p-3 opacity-10">
                <Shield className="w-20 h-20 text-white" />
            </div>

            <div className="relative z-10 text-center mb-3">
                <h3 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Current Risk Level</h3>
                <div className={`text-xl font-bold mt-1 ${config.color}`}>{config.label}</div>
            </div>

            <div className="relative flex-1 flex flex-col items-center justify-center">
                <canvas ref={canvasRef} style={{ width: '100%', height: '160px' }} className="max-w-[250px]" />

                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-center">
                    <motion.div
                        key={Math.round(displayScore)}
                        initial={{ scale: 0.95, opacity: 0.8 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className={`text-5xl font-bold tracking-tighter ${config.color}`}
                    >
                        {Math.round(displayScore)}
                    </motion.div>
                    <p className="text-[10px] text-zinc-500 font-mono mt-0.5">/ 100 RISK INDEX</p>
                </div>
            </div>

            <div className="flex justify-between text-[10px] font-medium text-zinc-600 mt-2 px-4 uppercase border-t border-zinc-800/50 pt-2">
                <span>Safe</span>
                <span>Warning</span>
                <span>Critical</span>
            </div>
        </div>
    );
}
