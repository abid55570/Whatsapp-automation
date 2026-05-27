"use client";

import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { useState } from "react";
import { toast, Toaster } from "sonner";

import { apiErrorMessage } from "@/lib/api";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: (failureCount, err: unknown) => {
              // Don't retry 4xx; retry 5xx/network at most once
              const status = (err as { response?: { status?: number } })
                ?.response?.status;
              if (status && status >= 400 && status < 500) return false;
              return failureCount < 1;
            },
            staleTime: 30_000,
            refetchOnWindowFocus: false,
          },
          mutations: {
            // POST/PATCH/DELETE: never retry — could double-create
            retry: 0,
          },
        },
        // Global toast for any unhandled query error
        queryCache: new QueryCache({
          onError: (err, query) => {
            if (query.meta?.silent) return;
            toast.error(apiErrorMessage(err));
          },
        }),
        // Global toast for any unhandled mutation error
        mutationCache: new MutationCache({
          onError: (err, _vars, _ctx, mutation) => {
            if (mutation.meta?.silent) return;
            toast.error(apiErrorMessage(err));
          },
        }),
      }),
  );

  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster
        position="top-center"
        richColors
        duration={3500}
        closeButton
        offset="64px"
        toastOptions={{ style: { marginTop: "env(safe-area-inset-top)" } }}
      />
    </QueryClientProvider>
  );
}
