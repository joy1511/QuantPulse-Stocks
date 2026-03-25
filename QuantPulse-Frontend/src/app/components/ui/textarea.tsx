import * as React from "react";

import { cn } from "./utils";

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "resize-none flex field-sizing-content min-h-16 w-full rounded-md border px-3 py-2 text-base transition-[color,box-shadow] outline-none md:text-sm",
        "bg-[rgba(30, 30, 30, 0.9)] border-[rgba(74, 158, 255, 0.15)] text-[#F0F0F0]",
        "placeholder:text-[#A0A0A0] backdrop-blur-sm",
        "focus-visible:border-[rgba(74, 158, 255, 0.12)] focus-visible:ring-[rgba(74, 158, 255, 0.12)] focus-visible:ring-[3px]",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export { Textarea };
