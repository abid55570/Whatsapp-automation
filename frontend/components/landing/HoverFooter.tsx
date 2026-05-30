"use client";

import React from "react";
import { Mail, Phone, MapPin, Twitter, Instagram, Linkedin, Globe } from "lucide-react";
import { TextHoverEffect, FooterBackgroundGradient } from "@/components/ui/hover-footer";

const footerLinks = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "Pricing", href: "#pricing" },
      { label: "FAQ", href: "#faq" },
      { label: "Start free trial", href: "/language?next=/signup" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About us", href: "#" },
      { label: "Customer stories", href: "#testimonials" },
      { label: "Careers", href: "#" },
      { label: "Live chat", href: "#", pulse: true },
    ],
  },
];

const contactInfo = [
  { icon: <Mail size={18} className="text-[#25d366]" />, text: "hello@whatly.app", href: "mailto:hello@whatly.app" },
  { icon: <Phone size={18} className="text-[#25d366]" />, text: "+91 98765 43210", href: "tel:+919876543210" },
  { icon: <MapPin size={18} className="text-[#25d366]" />, text: "Bengaluru, India" },
];

const socialLinks = [
  { icon: <Twitter size={20} />, label: "Twitter", href: "#" },
  { icon: <Instagram size={20} />, label: "Instagram", href: "#" },
  { icon: <Linkedin size={20} />, label: "LinkedIn", href: "#" },
  { icon: <Globe size={20} />, label: "Website", href: "#" },
];

export default function HoverFooter() {
  return (
    <footer className="relative m-4 h-fit overflow-hidden rounded-3xl bg-[#06140e] text-slate-300 md:m-8">
      <div className="relative z-40 mx-auto max-w-7xl p-10 md:p-14">
        <div className="grid grid-cols-1 gap-12 pb-12 md:grid-cols-2 md:gap-8 lg:grid-cols-4 lg:gap-16">
          {/* Brand */}
          <div className="flex flex-col space-y-4">
            <div className="flex items-center space-x-2">
              <span className="text-3xl font-extrabold text-[#25d366]">♥</span>
              <span className="font-display-serif text-3xl text-white">Whatly</span>
            </div>
            <p className="text-sm leading-relaxed text-slate-400">
              WhatsApp automation for ambitious Indian shops — auto-replies,
              orders and bookings in six languages.
            </p>
          </div>

          {/* Link sections */}
          {footerLinks.map((section) => (
            <div key={section.title}>
              <h4 className="mb-6 text-lg font-semibold text-white">{section.title}</h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.label} className="relative inline-block">
                    <a href={link.href} className="transition-colors hover:text-[#25d366]">
                      {link.label}
                    </a>
                    {"pulse" in link && link.pulse && (
                      <span className="absolute right-[-10px] top-0 h-2 w-2 animate-pulse rounded-full bg-[#25d366]" />
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* Contact */}
          <div>
            <h4 className="mb-6 text-lg font-semibold text-white">Contact us</h4>
            <ul className="space-y-4">
              {contactInfo.map((item, i) => (
                <li key={i} className="flex items-center space-x-3">
                  {item.icon}
                  {item.href ? (
                    <a href={item.href} className="transition-colors hover:text-[#25d366]">
                      {item.text}
                    </a>
                  ) : (
                    <span>{item.text}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <hr className="my-8 border-t border-white/10" />

        <div className="flex flex-col items-center justify-between space-y-4 text-sm md:flex-row md:space-y-0">
          <div className="flex space-x-6 text-slate-400">
            {socialLinks.map(({ icon, label, href }) => (
              <a key={label} href={href} aria-label={label} className="transition-colors hover:text-[#25d366]">
                {icon}
              </a>
            ))}
          </div>
          <p className="text-center text-slate-500 md:text-left">
            © {new Date().getFullYear()} Whatly. All rights reserved.
          </p>
        </div>
      </div>

      {/* Big hover text */}
      <div className="-mb-36 -mt-52 hidden h-[30rem] lg:flex">
        <TextHoverEffect text="Whatly" className="z-50" />
      </div>

      <FooterBackgroundGradient />
    </footer>
  );
}
