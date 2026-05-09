import { useToast } from "@/hooks/use-toast"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <div className="fixed top-0 right-0 z-50 flex flex-col gap-2 p-4">
      {toasts.map(function ({ id, title, description, action, ...props }) {
        return (
          <div
            key={id}
            className="bg-white border rounded-lg shadow-lg p-4 w-80"
            {...props}
          >
            <div className="flex flex-col space-y-2">
              {title && <div className="font-semibold">{title}</div>}
              {description && <div className="text-sm text-gray-600">{description}</div>}
              {action}
            </div>
          </div>
        )
      })}
    </div>
  )
}
