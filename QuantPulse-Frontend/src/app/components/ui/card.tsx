import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "./utils";

const cardVariants = cva(
  "flex flex-col gap-6 backdrop-blur-xl transition-all duration-300",
  {
    variants: {
      variant: {
        default: "rounded-xl border bg-[rgba(30, 30, 30, 0.9)] border-[rgba(74, 158, 255, 0.15)] text-[#F0F0F0] shadow-lg shadow-black/5",
        elevated: "rounded-[1.25rem] border border-[rgba(74, 158, 255, 0.15)] bg-[rgba(30, 30, 30, 0.9)] text-[#F0F0F0] shadow-xl shadow-blue-900/5 hover:shadow-blue-900/10 hover:bg-[rgba(30, 30, 30, 0.9)] hover:-translate-y-0.5",
        subtle: "rounded-[0.75rem] border border-[rgba(74, 158, 255, 0.15)] bg-[rgba(30, 30, 30, 0.9)] text-[#F0F0F0] shadow-sm",
        flat: "rounded-2xl border-0 bg-[rgba(30, 30, 30, 0.9)] text-[#F0F0F0]",
        glass: "rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(30, 30, 30, 0.9)] text-[#F0F0F0] shadow-lg shadow-black/5 backdrop-blur-2xl",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Card({ className, variant, ...props }: React.ComponentProps<"div"> & VariantProps<typeof cardVariants>) {
  return (
    <div
      data-slot="card"
      className={cn(cardVariants({ variant, className }))}
      {...props}
    />
  );
}

function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 pt-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        className,
      )}
      {...props}
    />
  );
}

function CardTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <h4
      data-slot="card-title"
      className={cn("leading-none", className)}
      {...props}
    />
  );
}

function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <p
      data-slot="card-description"
      className={cn("text-muted-foreground", className)}
      {...props}
    />
  );
}

function CardAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className,
      )}
      {...props}
    />
  );
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-content"
      className={cn("px-6 [&:last-child]:pb-6", className)}
      {...props}
    />
  );
}

function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-footer"
      className={cn("flex items-center px-6 pb-6 [.border-t]:pt-6", className)}
      {...props}
    />
  );
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
};
