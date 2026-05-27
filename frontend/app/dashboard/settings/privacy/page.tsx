"use client";

import {
  AlertTriangle,
  ArrowLeft,
  Download,
  Loader2,
  Shield,
  Trash2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { apiErrorMessage } from "@/lib/api";
import { downloadAccountExport, useDeleteAccount } from "@/lib/queries";
import { useAuthStore } from "@/stores/auth";

export default function PrivacySettingsPage() {
  const router = useRouter();
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const deleteAccount = useDeleteAccount();
  const [exporting, setExporting] = useState(false);
  const [confirmStep, setConfirmStep] = useState(0);

  async function handleExport() {
    setExporting(true);
    try {
      await downloadAccountExport();
      toast.success("Export downloaded");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    } finally {
      setExporting(false);
    }
  }

  async function handleDelete() {
    if (confirmStep < 2) {
      setConfirmStep(confirmStep + 1);
      setTimeout(() => setConfirmStep(0), 5000);
      return;
    }
    try {
      await deleteAccount.mutateAsync();
      toast.success("Account deleted. Data wiped in 30 days.");
      clearAuth();
      router.replace("/");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <div className="animate-fade-in pb-8">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-brand-600" />
            <h1 className="text-xl font-bold text-slate-900">
              Privacy & Data
            </h1>
          </div>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {/* Export */}
        <section className="card">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Download className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h2 className="font-semibold text-slate-900">Export your data</h2>
              <p className="text-xs text-slate-600 mt-0.5">
                Download a ZIP with all your messages, contacts, orders. JSON
                format.
              </p>
            </div>
          </div>
          <Button
            onClick={handleExport}
            loading={exporting}
            variant="secondary"
            fullWidth
          >
            {exporting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            Download data export
          </Button>
          <p className="text-[11px] text-slate-500 mt-2">
            Includes: user profile, business, contacts, conversations,
            messages, orders. Excludes secrets like access tokens.
          </p>
        </section>

        {/* Delete account */}
        <section className="card border-2 border-red-200 bg-red-50">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <div className="flex-1">
              <h2 className="font-semibold text-red-900">Delete account</h2>
              <p className="text-xs text-red-800 mt-0.5">
                Permanently removes your data after 30-day retention.
              </p>
            </div>
          </div>

          <ul className="text-xs text-red-800 list-disc pl-5 mb-3 space-y-1">
            <li>Account deactivated immediately</li>
            <li>Auto-replies stop</li>
            <li>30-day retention then permanent wipe</li>
            <li>You cannot undo this</li>
            <li>Export your data first if you want a copy</li>
          </ul>

          <Button
            onClick={handleDelete}
            loading={deleteAccount.isPending}
            variant="danger"
            fullWidth
          >
            <Trash2 className="h-4 w-4" />
            {confirmStep === 0 && "Delete my account"}
            {confirmStep === 1 && "Tap again to confirm..."}
            {confirmStep === 2 && "Are you absolutely sure?"}
          </Button>
          {confirmStep > 0 && (
            <p className="text-[11px] text-red-700 mt-2 text-center">
              Cancels in 5 seconds if you don't tap
            </p>
          )}
        </section>

        <p className="text-[11px] text-center text-slate-500 leading-relaxed mt-6">
          We process data under India's Digital Personal Data Protection Act,
          2023. See{" "}
          <a href="/privacy" className="underline">
            Privacy Policy
          </a>{" "}
          for details. Contact:{" "}
          <a
            href="mailto:privacy@example.com"
            className="underline"
          >
            privacy@example.com
          </a>
        </p>
      </div>
    </div>
  );
}
