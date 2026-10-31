"use client";

import { Eye, EyeOff } from "lucide-react";
import { useState, type ComponentProps } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/**
 * Password input with a show or hide toggle (§7.5.2). The toggle is a real button, so it is
 * reachable by keyboard, has a 44 px target and announces its state with aria-pressed.
 */
export function PasswordInput({
  id,
  className,
  ...props
}: Omit<ComponentProps<"input">, "type"> & { id: string }) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="relative">
      <Input
        id={id}
        type={visible ? "text" : "password"}
        className={cn("pr-12", className)}
        {...props}
      />
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute inset-y-0 right-0"
        aria-label="Show password"
        aria-pressed={visible}
        aria-controls={id}
        onClick={() => setVisible((value) => !value)}
      >
        {visible ? (
          <EyeOff aria-hidden="true" className="size-5" />
        ) : (
          <Eye aria-hidden="true" className="size-5" />
        )}
      </Button>
    </div>
  );
}
