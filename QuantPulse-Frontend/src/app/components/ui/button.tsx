import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "./utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default: "bg-[#1A6FD4] text-white hover:bg-[#2A7FE8] shadow-sm shadow-blue-500/20 rounded-lg hover:rounded-xl active:scale-[0.98] transition-all duration-300",
        destructive:
          "bg-destructive text-white hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60 rounded-lg",
        outline:
          "border border-[rgba(74, 158, 255, 0.15)] bg-transparent text-zinc-200 hover:bg-[rgba(74,158,255,0.15)] hover:border-[rgba(74, 158, 255, 0.15)] rounded-xl",
        secondary:
          "bg-[rgba(30, 30, 30, 0.9)] text-zinc-200 border border-[rgba(74, 158, 255, 0.15)] hover:bg-[rgba(30, 30, 30, 0.9)] rounded-md",
        ghost:
          "hover:bg-[rgba(74,158,255,0.1)] hover:text-[#F0F0F0] rounded-lg",
        link: "text-[#4A9EFF] underline-offset-4 hover:underline rounded-none",
        fintech: "bg-transparent border border-[#1A6FD4]/40 text-[#4A9EFF] hover:bg-[#1A6FD4]/10 hover:border-[#1A6FD4]/60 rounded-2xl",
        prominent: "bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white shadow-md hover:shadow-blue-500/30 hover:-translate-y-0.5 rounded-2xl border border-[#2A2A2A]",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-11 px-8 has-[>svg]:px-5 text-base",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
