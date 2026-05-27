"use client";

import { Loader2, Search, ShieldCheck, ShieldOff } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { useAdminUsers, useUpdateAdminUser } from "@/lib/queries";
import type { AdminUserRow } from "@/types/api";

function UserRow({ user }: { user: AdminUserRow }) {
  const update = useUpdateAdminUser();
  const [busy, setBusy] = useState(false);

  const toggle = async (field: "is_active" | "is_superuser") => {
    setBusy(true);
    try {
      await update.mutateAsync({
        userId: user.id,
        data: { [field]: !user[field] },
      });
    } catch (e) {
      toast.error(`Failed: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <tr className="border-t border-slate-100">
      <td className="py-2 px-3">
        <div className="font-medium text-slate-900">{user.phone}</div>
        {user.full_name && (
          <div className="text-xs text-slate-500">{user.full_name}</div>
        )}
      </td>
      <td className="py-2 px-3 text-xs text-slate-600">
        {user.email || "—"}
      </td>
      <td className="py-2 px-3">
        <span
          className={
            user.is_active
              ? "px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded"
              : "px-2 py-0.5 bg-slate-100 text-slate-500 text-xs rounded"
          }
        >
          {user.is_active ? "active" : "inactive"}
        </span>
      </td>
      <td className="py-2 px-3">
        {user.is_superuser && (
          <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded">
            superuser
          </span>
        )}
      </td>
      <td className="py-2 px-3 text-right">
        <div className="flex justify-end gap-1">
          <button
            disabled={busy}
            onClick={() => toggle("is_superuser")}
            className="p-1.5 hover:bg-slate-100 rounded disabled:opacity-50"
            title={user.is_superuser ? "Revoke superuser" : "Grant superuser"}
          >
            {user.is_superuser ? (
              <ShieldOff className="h-4 w-4 text-red-500" />
            ) : (
              <ShieldCheck className="h-4 w-4 text-amber-500" />
            )}
          </button>
          <button
            disabled={busy}
            onClick={() => toggle("is_active")}
            className="px-2 py-1 text-xs hover:bg-slate-100 rounded disabled:opacity-50"
          >
            {user.is_active ? "Deactivate" : "Activate"}
          </button>
        </div>
      </td>
    </tr>
  );
}

export default function AdminUsersPage() {
  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 50;
  const { data, isLoading } = useAdminUsers(q, limit, offset);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h1 className="text-2xl font-bold text-slate-900">Users</h1>
        <div className="relative">
          <Search className="h-4 w-4 absolute left-2.5 top-2.5 text-slate-400" />
          <input
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setOffset(0);
            }}
            placeholder="Search phone, name, email"
            className="pl-8 pr-3 py-2 border border-slate-300 rounded-lg text-sm w-full sm:w-64"
          />
        </div>
      </div>

      {isLoading || !data ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        </div>
      ) : (
        <>
          <div className="bg-white border border-slate-200 rounded-xl overflow-x-auto">
            <table className="w-full text-sm min-w-[640px]">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="text-left py-2 px-3">User</th>
                  <th className="text-left py-2 px-3">Email</th>
                  <th className="text-left py-2 px-3">Status</th>
                  <th className="text-left py-2 px-3">Role</th>
                  <th className="text-right py-2 px-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500">
                      No users found.
                    </td>
                  </tr>
                ) : (
                  data.items.map((u: AdminUserRow) => (
                    <UserRow key={u.id} user={u} />
                  ))
                )}
              </tbody>
            </table>
          </div>
          <Pagination
            total={data.total}
            offset={offset}
            limit={limit}
            hasMore={data.has_more}
            onChange={setOffset}
          />
        </>
      )}
    </div>
  );
}

function Pagination({
  total,
  offset,
  limit,
  hasMore,
  onChange,
}: {
  total: number;
  offset: number;
  limit: number;
  hasMore: boolean;
  onChange: (offset: number) => void;
}) {
  return (
    <div className="flex items-center justify-between text-sm text-slate-600">
      <div>
        Showing {offset + 1}–{Math.min(offset + limit, total)} of {total}
      </div>
      <div className="flex gap-2">
        <button
          disabled={offset === 0}
          onClick={() => onChange(Math.max(0, offset - limit))}
          className="px-3 py-1.5 border border-slate-300 rounded disabled:opacity-40"
        >
          Prev
        </button>
        <button
          disabled={!hasMore}
          onClick={() => onChange(offset + limit)}
          className="px-3 py-1.5 border border-slate-300 rounded disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
