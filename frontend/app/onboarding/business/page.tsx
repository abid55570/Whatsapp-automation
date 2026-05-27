"use client";

import { ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { BusinessTypeGrid } from "@/components/BusinessTypeCard";
import { LanguageChips } from "@/components/LanguageChip";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiErrorMessage } from "@/lib/api";
import { useCreateBusiness } from "@/lib/queries";
import type { BusinessType, Language } from "@/types/api";

export default function BusinessSetupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [businessType, setBusinessType] = useState<BusinessType | null>(null);
  const [languages, setLanguages] = useState<Language[]>([
    "english",
    "hinglish",
  ]);

  const mutation = useCreateBusiness();

  function toggleLanguage(lang: Language) {
    setLanguages((prev) =>
      prev.includes(lang) ? prev.filter((l) => l !== lang) : [...prev, lang],
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!businessType) {
      toast.error("Pick your business type");
      return;
    }
    if (languages.length === 0) {
      toast.error("Pick at least one language your customers use");
      return;
    }
    try {
      await mutation.mutateAsync({
        name: name.trim(),
        business_type: businessType,
        languages,
      });
      toast.success("Business profile created");
      router.replace("/onboarding/whatsapp");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">
        Tell us about your business
      </h1>
      <p className="text-slate-600 text-sm mb-6">
        Takes 30 seconds. You can edit anything later.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Input
          label="Business name"
          placeholder="Sharma Salon & Spa"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          minLength={2}
          maxLength={200}
          autoFocus
        />

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            What kind of business?
          </label>
          <BusinessTypeGrid
            selected={businessType}
            onChange={setBusinessType}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Languages your customers use
          </label>
          <p className="text-xs text-slate-500 mb-3">
            Auto-replies handle all selected languages — including mixed messages
          </p>
          <LanguageChips selected={languages} onToggle={toggleLanguage} />
        </div>

        <Button
          type="submit"
          loading={mutation.isPending}
          fullWidth
          size="lg"
          disabled={!name.trim() || !businessType || languages.length === 0}
        >
          Continue
          <ArrowRight className="h-5 w-5" />
        </Button>
      </form>
    </div>
  );
}
