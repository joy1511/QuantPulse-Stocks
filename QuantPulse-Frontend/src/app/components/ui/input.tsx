import * as React from "react";

import { cn } from "./utils";

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-9 w-full min-w-0 rounded-md border px-3 py-1 text-base transition-[color,box-shadow] outline-none md:text-sm",
        "bg-[rgba(30, 30, 30, 0.9)] border-[rgba(74, 158, 255, 0.15)] text-[#F0F0F0]",
        "placeholder:text-[#A0A0A0] backdrop-blur-sm",
        "focus-visible:border-[rgba(74, 158, 255, 0.12)] focus-visible:ring-[rgba(74, 158, 255, 0.12)] focus-visible:ring-[3px]",
        "disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
        "file:text-zinc-300 file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
