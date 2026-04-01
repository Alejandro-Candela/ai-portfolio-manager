"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/portfolio", label: "Portfolio" },
  { href: "/pipeline", label: "Pipeline" },
  { href: "/intake", label: "New Use Case" },
  { href: "/analytics", label: "Analytics" },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="container mx-auto flex items-center justify-between">
        <Link href="/portfolio" className="font-semibold text-gray-900 text-lg">
          AI Portfolio Manager
        </Link>
        <ul className="flex gap-6">
          {links.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`text-sm font-medium transition-colors ${
                  pathname.startsWith(href)
                    ? "text-blue-600"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
