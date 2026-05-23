import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

const DialogContext = React.createContext<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}>({ isOpen: false, setIsOpen: () => {} })

const Dialog = ({ children, ...props }: React.ComponentProps<"div"> & { open?: boolean; onOpenChange?: (open: boolean) => void }) => {
  const [isOpen, setIsOpen] = React.useState(props.open ?? false)

  React.useEffect(() => {
    if (props.open !== undefined) {
      setIsOpen(props.open)
    }
  }, [props.open])

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    props.onOpenChange?.(open)
  }

  return (
    <DialogContext.Provider value={{ isOpen, setIsOpen: handleOpenChange }}>
      {children}
    </DialogContext.Provider>
  )
}

const DialogTrigger = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { asChild?: boolean }>(({ children, ...props }, ref) => {
  const { setIsOpen } = React.useContext(DialogContext)

  return (
    <div ref={ref} onClick={() => setIsOpen(true)} {...props}>
      {children}
    </div>
  )
})
DialogTrigger.displayName = "DialogTrigger"

const DialogContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, children, ...props }, ref) => {
  const { isOpen, setIsOpen } = React.useContext(DialogContext)

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/80" onClick={() => setIsOpen(false)} />
      <div className="fixed left-[50%] top-[50%] z-50 translate-x-[-50%] translate-y-[-50%] w-full max-w-lg">
        <div ref={ref} className={cn("relative bg-slate-900 border border-slate-800 rounded-lg shadow-lg p-6", className)} {...props}>
          <button onClick={() => setIsOpen(false)} className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
            <X className="h-4 w-4 text-white" />
          </button>
          {children}
        </div>
      </div>
    </>
  )
})
DialogContent.displayName = "DialogContent"

const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left mb-4", className)} {...props} />
)
DialogHeader.displayName = "DialogHeader"

const DialogTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(({ className, ...props }, ref) => (
  <h2 ref={ref} className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
))
DialogTitle.displayName = "DialogTitle"

export { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle }
