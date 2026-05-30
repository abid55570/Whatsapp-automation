// Content + assets for the dark cinematic landing page.

/** Cinematic abstract background video (Mux HLS). Used in the footer. */
export const HLS_SRC =
  "https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8";

/** Fullscreen MP4 used as the cinematic hero background (4K starry night sky). */
export const HERO_VIDEO =
  "https://videos.pexels.com/video-files/13818901/13818901-uhd_3246_2160_30fps.mp4";

/** Hotlinkable Unsplash CDN URL from a photo id (no API key required). */
export const unsplash = (id: string, w = 900) =>
  `https://images.unsplash.com/photo-${id}?w=${w}&q=80&auto=format&fit=crop`;

/** Hotlinkable Pexels CDN URL from a photo id (no API key required). */
export const pexels = (id: number, w = 1000) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

/** Portrait-cropped Pexels URL (for headshots / avatars). */
export const pexelsPortrait = (id: number, w = 640, h = 800) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}&h=${h}&fit=crop`;

/** Friendly illustrated (comic) avatar from a seed — DiceBear, no API key,
 *  CORS-enabled so it can also be drawn into the phone's WebGL chat canvas. */
export const avatar = (seed: string) =>
  `https://api.dicebear.com/9.x/avataaars/png?seed=${encodeURIComponent(
    seed
  )}&size=240&radius=50&backgroundColor=b9f0d4,c8f5dd,a6e9c6,d9fbe8`;

export const SIGNUP_HREF = "/language?next=/signup";

/** Nav items: `section` scrolls within the page, `href` routes to a page. */
export const NAV_LINKS: { label: string; section?: string; href?: string }[] = [
  { label: "Home", section: "hero" },
  { label: "Features", section: "features" },
  { label: "Pricing", section: "pricing" },
  { label: "Blog", href: "/blog" },
  { label: "FAQ", section: "faq" },
];

/** Words cycled on the loading screen. */
export const LOADING_WORDS = ["Reply", "Sell", "Grow"];

/** Business types cycled in the hero headline. */
export const HERO_BUSINESSES = ["Kirana", "Restaurant", "Salon", "Clinic"];

/** Bento use-cases (alternating 7/5/5/7 column spans). */
export interface UseCase {
  title: string;
  blurb: string;
  image: string;
  span: 5 | 7;
}

export const USE_CASES: UseCase[] = [
  {
    title: "Restaurants",
    blurb: "Share the menu, take orders, confirm pickup — automatically.",
    image: unsplash("1556740738-b6a63e27c4df", 1400),
    span: 7,
  },
  {
    title: "Kirana Stores",
    blurb: "“2 atta, 1 dal” → parsed, totalled, ready for COD.",
    image: unsplash("1601050690597-df0568f70950", 1000),
    span: 5,
  },
  {
    title: "Salons",
    blurb: "Services, bookings and reminders without a single call.",
    image: unsplash("1559599101-f09722fb4948", 1000),
    span: 5,
  },
  {
    title: "Clinics",
    blurb: "Hours, appointments and FAQs answered the moment they ask.",
    image: unsplash("1604342427523-189b17048839", 1400),
    span: 7,
  },
];

/** "Live in 10 minutes" steps, shown as horizontal pills. */
export const STEPS = [
  {
    n: 1,
    title: "Sign up free",
    body: "Phone number → verify on WhatsApp → 14-day trial. No credit card.",
  },
  {
    n: 2,
    title: "Connect WhatsApp Business",
    body: "One tap via Meta’s official Embedded Signup. Your data stays yours.",
  },
  {
    n: 3,
    title: "Pick auto-replies",
    body: "12 ready templates — price, timings, menu, location. Edit answers, done.",
  },
  {
    n: 4,
    title: "Customers get instant answers",
    body: "The bot replies 24/7 in the customer’s language. You watch the inbox.",
  },
];

/** Bento "works" grid — Indian SMB types + the pain Whatly solves for each. */
export interface GalleryItem {
  title: string;
  /** Pain-point fact shown on hover (what they lose without fast replies). */
  fact: string;
  image: string;
  rotation: number;
  column: 0 | 1;
}

export const GALLERY: GalleryItem[] = [
  {
    title: "Restaurants",
    fact: "Diners order from whoever replies first — a late reply at the dinner rush is a lost table.",
    image: pexels(31071253, 1200),
    rotation: -3,
    column: 0,
  },
  {
    title: "Gyms & studios",
    fact: "Most membership enquiries go cold if no one answers within the hour.",
    image: pexels(29526371, 1000),
    rotation: 2,
    column: 1,
  },
  {
    title: "Clinics",
    fact: "Patients book the clinic that answers now — not the one that calls back later.",
    image: pexels(33812025, 1000),
    rotation: 3,
    column: 0,
  },
  {
    title: "Salons & spas",
    fact: "A booking message missed at peak hours is an empty chair you can't refill.",
    image: pexels(7922651, 1000),
    rotation: -2,
    column: 1,
  },
  {
    title: "Kirana stores",
    fact: "Customers reorder from whoever confirms stock and price fastest.",
    image: pexels(26309839, 1000),
    rotation: -4,
    column: 0,
  },
  {
    title: "Boutiques",
    fact: "Shoppers asking for sizes buy from the first store that replies.",
    image: pexels(8386651, 1200),
    rotation: 2,
    column: 1,
  },
];

/** Testimonials from Indian SMB owners — split across two parallax columns. */
export interface Testimonial {
  quote: string;
  name: string;
  business: string;
  location: string;
  /** Business category — shown as a tag so the customer variety is clear. */
  type: string;
  initials: string;
  /** Portrait photo — used by the mobile circular-carousel layout. */
  image: string;
  rotation: number;
  column: 0 | 1;
}

export const TESTIMONIALS: Testimonial[] = [
  {
    quote:
      "Pehle har order phone pe lena padta tha. Ab Whatly khud reply karta hai — main bas cooking pe focus karta hoon.",
    name: "Rajesh Kumar",
    business: "Tandoori House",
    location: "Delhi",
    type: "Restaurant",
    initials: "RK",
    image: avatar("Rajesh Kumar"),
    rotation: -2,
    column: 0,
  },
  {
    quote:
      "Membership queries, class timings, renewals — all handled on WhatsApp before I even reach the floor.",
    name: "Karan Verma",
    business: "FitZone Studio",
    location: "Hyderabad",
    type: "Gym & fitness",
    initials: "KV",
    image: avatar("Karan Verma"),
    rotation: 2,
    column: 1,
  },
  {
    quote:
      "Hinglish orders bhi samajh leta hai. '2 atta 1 dal' type karo, total ready. Customers ko bahut pasand aaya.",
    name: "Suresh Sharma",
    business: "Sharma Kirana",
    location: "Mumbai",
    type: "Kirana store",
    initials: "SS",
    image: avatar("Suresh Sharma"),
    rotation: 3,
    column: 0,
  },
  {
    quote:
      "My evening rush meant 30 missed messages. Now every client gets slots instantly and I book them right in chat.",
    name: "Anjali Sharma",
    business: "Glow Salon & Spa",
    location: "Pune",
    type: "Salon & spa",
    initials: "AS",
    image: avatar("Anjali Sharma"),
    rotation: -3,
    column: 1,
  },
  {
    quote:
      "Customers ping for kurti sizes and prices all day. Whatly shares the catalogue and books trials — I just stitch.",
    name: "Riya Choudhary",
    business: "Riya Couture",
    location: "Jaipur",
    type: "Boutique",
    initials: "RC",
    image: avatar("Riya Choudhary"),
    rotation: 2,
    column: 0,
  },
  {
    quote:
      "Appointment reminders alone cut my no-shows by half. Hours and FAQs are answered 24/7. Worth every rupee.",
    name: "Dr. Mehta",
    business: "CityCare Clinic",
    location: "Kochi",
    type: "Clinic",
    initials: "DM",
    image: avatar("Dr. Mehta"),
    rotation: -2,
    column: 1,
  },
];

/** One WhatsApp chat bubble. "out" = customer (right, green), "in" = the bot. */
export interface ChatMsg {
  side: "in" | "out";
  text: string;
  bot?: boolean;
}

/** A use-case shown in the scroll-driven phone showcase. */
export interface Showcase {
  key: string;
  emoji: string;
  title: string;
  blurb: string;
  /** Short feature bullets shown under the blurb. */
  points: string[];
  phoneName: string;
  /** Avatar shown in the WhatsApp chat header (square portrait crop). */
  pfp: string;
  chat: ChatMsg[];
}

export const SHOWCASE: Showcase[] = [
  {
    key: "restaurant",
    emoji: "🍽️",
    title: "Restaurants",
    blurb: "Your busiest hours shouldn't mean missed orders. Whatly shares the menu, takes the order, totals it and locks in a pickup time — all inside WhatsApp, while you cook.",
    points: [
      "Auto-sends today's menu & live prices",
      "Captures and totals orders in chat",
      "Confirms pickup time + payment method",
      "Never leaves a hungry customer on read",
    ],
    phoneName: "Tandoori House",
    pfp: avatar("Tandoori House"),
    chat: [
      { side: "out", text: "Aaj ka menu bhejo?" },
      { side: "in", bot: true, text: "🍽️ Butter Naan ₹40 · Paneer Tikka ₹220 · Dal Makhani ₹180. Order karein?" },
      { side: "out", text: "2 butter naan, 1 paneer tikka" },
      { side: "in", bot: true, text: "📝 ₹300 · Ready in 25 min. Pay on pickup?" },
      { side: "out", text: "haan" },
      { side: "in", text: "✅ Order #R210 confirmed! See you at 7 PM." },
    ],
  },
  {
    key: "kirana",
    emoji: "🛒",
    title: "Kirana Stores",
    blurb: "Customers type the way they talk. Whatly reads messy Hindi & Hinglish lists, checks stock, totals the basket and queues it for cash-on-delivery — no app, no forms.",
    points: [
      "Understands Hindi & Hinglish orders",
      "Checks stock and quotes live prices",
      "Auto-totals the basket instantly",
      "Queues cash-on-delivery pickups",
    ],
    phoneName: "Sharma Kirana",
    pfp: avatar("Sharma Kirana"),
    chat: [
      { side: "out", text: "kitne ka hai atta?" },
      { side: "in", bot: true, text: "Atta 5kg ₹250, 1kg ₹55. ✅ In stock!" },
      { side: "out", text: "2 atta, 1 toor dal bhejo" },
      { side: "in", bot: true, text: "📝 Order ₹680 · Pickup by 5 PM. Reply YES to confirm." },
      { side: "out", text: "haan" },
      { side: "in", text: "✅ Order #1234 confirmed! 💵 Cash on pickup." },
    ],
  },
  {
    key: "salon",
    emoji: "💇",
    title: "Salons",
    blurb: "Stop pausing mid-haircut to answer the phone. Whatly shows open slots, books the appointment and sends the reminder — so your chair stays full and no-shows drop.",
    points: [
      "Shows live open slots instantly",
      "Books & reschedules right in chat",
      "Sends automatic visit reminders",
      "Cuts no-shows without a phone call",
    ],
    phoneName: "Glow Salon",
    pfp: avatar("Glow Salon"),
    chat: [
      { side: "out", text: "Kal haircut ka slot hai?" },
      { side: "in", bot: true, text: "Kal khaali: 11 AM, 2 PM, 5 PM. Kaunsa karein?" },
      { side: "out", text: "2 PM theek hai" },
      { side: "in", bot: true, text: "✅ Booked — Haircut, kal 2 PM. Reminder bhej denge 🔔" },
    ],
  },
  {
    key: "clinic",
    emoji: "🩺",
    title: "Clinics",
    blurb: "Patients ask the same things at all hours. Whatly answers timings and FAQs instantly, books OPD slots and flags urgent cases — so your front desk breathes easier.",
    points: [
      "Answers hours & FAQs 24/7",
      "Books and confirms OPD appointments",
      "Sends visit & follow-up reminders",
      "Flags urgent messages for staff",
    ],
    phoneName: "CityCare Clinic",
    pfp: avatar("CityCare Clinic"),
    chat: [
      { side: "out", text: "Doctor aaj available hain?" },
      { side: "in", bot: true, text: "Aaj OPD 4–8 PM. Appointment book karein?" },
      { side: "out", text: "haan, 6 baje" },
      { side: "in", bot: true, text: "✅ Token #18 · 6:00 PM. SMS bhej diya 📩" },
    ],
  },
];

export const STATS = [
  { value: "6", label: "Languages supported" },
  { value: "₹399", label: "Starts from / month" },
  { value: "10 min", label: "To go live" },
  { value: "14-day", label: "Free trial" },
];

export interface Plan {
  name: string;
  price: number;
  conv: number;
  features: string[];
  recommended?: boolean;
}

export const PLANS: Plan[] = [
  {
    name: "Starter",
    price: 399,
    conv: 1000,
    features: [
      "Auto-reply (6 languages)",
      "1,000 conversations/mo",
      "FAQ bot",
      "Inbox + dashboard",
      "Google Sheets sync",
    ],
  },
  {
    name: "Growth",
    price: 999,
    conv: 3000,
    recommended: true,
    features: [
      "Everything in Starter",
      "3,000 conversations/mo",
      "Orders + Pickup flow",
      "Bookings + Calendar",
      "Razorpay payment links",
      "Analytics",
    ],
  },
  {
    name: "Pro",
    price: 1999,
    conv: 6000,
    features: [
      "Everything in Growth",
      "6,000 conversations/mo",
      "Broadcasts",
      "API + Webhooks",
      "Priority support",
    ],
  },
];

export const FAQS = [
  {
    q: "Will my customers know it’s a bot?",
    a: "They get instant, accurate answers in their language. Most assume it’s you typing fast. You can mark replies with 🤖 if you want full transparency.",
  },
  {
    q: "Do I need a special WhatsApp number?",
    a: "Yes — a WhatsApp Business number (free, from the WhatsApp Business app). We connect to it via Meta’s official integration.",
  },
  {
    q: "What if a customer asks something my FAQs don’t cover?",
    a: "The message lands in your inbox marked ‘Needs reply’. You reply manually, or enable the AI add-on (₹699/mo) for smart fallback replies.",
  },
  {
    q: "Which languages exactly?",
    a: "English, Hindi (देवनागरी), Hinglish, Bengali, Urdu, Bhojpuri. The bot detects what the customer wrote and replies in the same language.",
  },
  {
    q: "How do I add new items / FAQs?",
    a: "Edit directly in the dashboard, or edit your Google Sheet — the bot auto-syncs every 15 minutes. Most owners prefer the Sheet.",
  },
  {
    q: "Is there a setup fee or commitment?",
    a: "No setup fee. No commitment. 14-day free trial. Card not required for the trial.",
  },
];

export const SOCIALS = [
  { label: "Twitter", href: "https://twitter.com" },
  { label: "LinkedIn", href: "https://linkedin.com" },
  { label: "Instagram", href: "https://instagram.com" },
  { label: "YouTube", href: "https://youtube.com" },
];
