import * as React from "react"
import { X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

interface DialogContextType {
    open: boolean
    onOpenChange: (open: boolean) => void
}

const DialogContext = React.createContext<DialogContextType>({
    open: false,
    onOpenChange: () => { },
})

export const Dialog: React.FC<{
    children: React.ReactNode
    open: boolean
    onOpenChange: (open: boolean) => void
}> = ({ children, open, onOpenChange }) => {
    return (
        <DialogContext.Provider value={{ open, onOpenChange }}>
            {children}
        </DialogContext.Provider>
    )
}

export const DialogContent: React.FC<{
    children: React.ReactNode
    className?: string
}> = ({ children, className }) => {
    const { open, onOpenChange } = React.useContext(DialogContext)

    if (!open) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
            <div
                className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
                onClick={() => onOpenChange(false)}
            />
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                className={cn(
                    "relative w-full overflow-hidden rounded-xl border bg-background p-6 shadow-lg sm:rounded-2xl",
                    className
                )}
            >
                {children}
                <button
                    onClick={() => onOpenChange(false)}
                    className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
                >
                    <X className="h-4 w-4 text-zinc-400 hover:text-white" />
                    <span className="sr-only">Close</span>
                </button>
            </motion.div>
        </div>
    )
}

export const DialogHeader: React.FC<{
    children: React.ReactNode
    className?: string
}> = ({ children, className }) => {
    return (
        <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left", className)}>
            {children}
        </div>
    )
}

export const DialogTitle: React.FC<{
    children: React.ReactNode
    className?: string
}> = ({ children, className }) => {
    return (
        <h2 className={cn("text-lg font-semibold leading-none tracking-tight", className)}>
            {children}
        </h2>
    )
}
