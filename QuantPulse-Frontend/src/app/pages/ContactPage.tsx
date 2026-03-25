import { useState } from 'react';
import emailjs from '@emailjs/browser';
import { Card } from '@/app/components/ui/card';
import { Input } from '@/app/components/ui/input';
import { Textarea } from '@/app/components/ui/textarea';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Mail, Phone, MapPin, Send, Clock, MessageSquare, CheckCircle, AlertCircle, Loader2, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';

// ── EmailJS config ──────────────────────────────────────────────────
// Sign up at https://www.emailjs.com, create a service + template, paste IDs below
const EMAILJS_SERVICE_ID  = import.meta.env.VITE_EMAILJS_SERVICE_ID  || 'YOUR_SERVICE_ID';
const EMAILJS_TEMPLATE_ID = import.meta.env.VITE_EMAILJS_TEMPLATE_ID || 'YOUR_TEMPLATE_ID';
const EMAILJS_PUBLIC_KEY  = import.meta.env.VITE_EMAILJS_PUBLIC_KEY  || 'YOUR_PUBLIC_KEY';
// ───────────────────────────────────────────────────────────────────

export function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [status, setStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const faqs = [
    {
      q: "What is QuantPulse India and who is it for?",
      a: "QuantPulse India is an AI-powered stock market research platform built for NSE. It combines LSTM neural networks, Hidden Markov Model regime detection, and multi-agent AI analysis to generate research reports on individual stocks. It is designed for retail investors, students, and analysts who want data-driven insights — not trading signals."
    },
    {
      q: "Is this financial advice? Can I use this to make trading decisions?",
      a: "No. QuantPulse India is strictly a research and educational tool. All outputs — LSTM probabilities, regime labels, AI reports — are analytical signals based on historical data and statistical models. They do not constitute financial advice. Stocks are inherently unpredictable and past patterns do not guarantee future results."
    },
    {
      q: "How does the LSTM prediction work?",
      a: "The LSTM model is a Bidirectional LSTM trained on NSE stock data. It takes the last 60 days of 6 technical features (RSI, MACD, Volatility, Bollinger %B, Normalized ATR, Log Returns) and outputs a probability between 0 and 1. Above 0.55 is Bullish Outlook, below 0.45 is Bearish Outlook, and in between is Neutral."
    },
    {
      q: "What is Market Regime and how is it detected?",
      a: "Market Regime is detected using a Hidden Markov Model (HMM) trained on Nifty 50 returns. It classifies the current market state as Bull, Bear, or Sideways based on the statistical distribution of recent returns. This helps contextualize individual stock signals — a Bullish LSTM signal in a Bear regime carries different weight than in a Bull regime."
    },
    {
      q: "Why does the analysis sometimes show 'AI agent analysis unavailable'?",
      a: "The multi-agent debate (Fundamentalist, Technician, Risk Manager) uses the Groq API with a free-tier LLM. When the API quota is exceeded or the agents time out (25s limit), the system gracefully falls back to the LSTM + HMM technical report. The core analysis — price data, LSTM probability, regime, VIX, and technical indicators — is always real and always shown."
    },
    {
      q: "Which stocks are supported?",
      a: "All NSE-listed stocks are supported. Enter the NSE ticker symbol (e.g., RELIANCE, TCS, HDFCBANK, INFY). The system fetches 2 years of daily OHLCV data and runs the full analysis pipeline. Indices like NIFTY50 are also supported for regime context."
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('sending');

    try {
      await emailjs.send(
        EMAILJS_SERVICE_ID,
        EMAILJS_TEMPLATE_ID,
        {
          name:    formData.name,
          email:   formData.email,
          title:   formData.subject,
          message: formData.message,
        },
        EMAILJS_PUBLIC_KEY
      );
      setStatus('success');
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (err: any) {
      console.error('EmailJS error:', err?.text || err?.message || err);
      setStatus('error');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const contactInfo = [
    {
      icon: Mail,
      label: 'Email Us',
      value: 'quantpulse.india@gmail.com',
      description: 'We\'ll respond within 24 hours'
    },
    {
      icon: Phone,
      label: 'Call Us',
      value: '+91 86394 11136',
      description: 'Mon-Fri, 9:00 AM - 6:00 PM IST'
    },
    {
      icon: MapPin,
      label: 'Visit Us',
      value: 'DTU, Delhi',
      description: 'India'
    }
  ];

  return (
    <div className="min-h-screen text-[#F0F0F0] p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl mb-4 text-[#F0F0F0]">Get in Touch</h1>
          <p className="text-lg text-[#A0A0A0] max-w-2xl mx-auto">
            Have questions about QuantPulse India? We're here to help.
            Reach out to our team and we'll get back to you as soon as possible.
          </p>
        </div>

        {/* Contact Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {contactInfo.map((info, index) => {
            const Icon = info.icon;
            return (
              <Card key={index} variant={index % 2 === 0 ? "subtle" : "default"} className="p-6 text-center hover:-translate-y-1 transition-transform duration-300">
                <div className="inline-flex p-3 rounded-lg bg-[rgba(74,158,255,0.1)] mb-4">
                  <Icon className="size-6 text-[#4A9EFF]" />
                </div>
                <h3 className="text-lg text-[#F0F0F0] mb-2">{info.label}</h3>
                <p className="text-[#A0A0A0] mb-1">{info.value}</p>
                <p className="text-sm text-[#A0A0A0]">{info.description}</p>
              </Card>
            );
          })}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Contact Form */}
          <Card variant="elevated" className="lg:col-span-2 p-8 border-none bg-[rgba(30, 30, 30, 0.9)] shadow-xl shadow-blue-900/5">
            <div className="flex items-center gap-2 mb-6">
              <MessageSquare className="size-6 text-[#4A9EFF]" />
              <h2 className="text-2xl text-[#F0F0F0]">Send Us a Message</h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-[#A0A0A0]">Full Name</Label>
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={handleChange}
                    className="bg-[#2A2A2A] border-[#2A2A2A] text-[#F0F0F0] placeholder:text-[#A0A0A0]"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-[#A0A0A0]">Email Address</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    className="bg-[#2A2A2A] border-[#2A2A2A] text-[#F0F0F0] placeholder:text-[#A0A0A0]"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject" className="text-[#A0A0A0]">Subject</Label>
                <Input
                  id="subject"
                  name="subject"
                  type="text"
                  placeholder="How can we help?"
                  value={formData.subject}
                  onChange={handleChange}
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-[#F0F0F0] placeholder:text-[#A0A0A0]"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="message" className="text-[#A0A0A0]">Message</Label>
                <Textarea
                  id="message"
                  name="message"
                  placeholder="Tell us more about your inquiry..."
                  value={formData.message}
                  onChange={handleChange}
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-[#F0F0F0] placeholder:text-[#A0A0A0] min-h-[150px]"
                  required
                />
              </div>

              {status === 'success' && (
                <div className="flex items-center gap-2 p-3 bg-[#4CAF7D]/10 border border-[#4CAF7D]/20 rounded-lg text-[#4CAF7D] text-sm">
                  <CheckCircle className="size-4 shrink-0" />
                  Message sent! We'll get back to you within 24 hours.
                </div>
              )}

              {status === 'error' && (
                <div className="flex items-center gap-2 p-3 bg-[#E05252]/10 border border-[#E05252]/20 rounded-lg text-[#E05252] text-sm">
                  <AlertCircle className="size-4 shrink-0" />
                  Failed to send. Please email us directly at quantpulse.india@gmail.com
                </div>
              )}

              <Button
                type="submit"
                disabled={status === 'sending' || status === 'success'}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-60"
              >
                {status === 'sending' ? (
                  <><Loader2 className="size-4 mr-2 animate-spin" />Sending...</>
                ) : status === 'success' ? (
                  <><CheckCircle className="size-4 mr-2" />Sent!</>
                ) : (
                  <><Send className="size-4 mr-2" />Send Message</>
                )}
              </Button>
            </form>
          </Card>

          {/* Company Info Sidebar */}
          <div className="space-y-6">
            <Card variant="subtle" className="p-6">
              <h3 className="text-lg font-medium text-[#F0F0F0] mb-4">About QuantPulse India</h3>
              <p className="text-sm text-[#A0A0A0] leading-relaxed mb-4">
                We're a team of aspiring data scientists, financial analysts, and engineers
                dedicated to democratizing AI-powered stock market analysis as a research deck for Indian traders.
              </p>
              <p className="text-sm text-[#A0A0A0] leading-relaxed">
                Our mission is to make sophisticated market intelligence accessible to everyone,
                helping traders make informed decisions with confidence.
              </p>
            </Card>

            <Card variant="flat" className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="size-5 text-[#4A9EFF]" />
                <h3 className="text-lg font-medium text-[#F0F0F0]">Business Hours</h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-[#A0A0A0]">Monday - Friday</span>
                  <span className="text-[#F0F0F0]">9:00 AM - 6:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#A0A0A0]">Saturday</span>
                  <span className="text-[#F0F0F0]">10:00 AM - 2:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#A0A0A0]">Sunday</span>
                  <span className="text-[#F0F0F0]">Closed</span>
                </div>
              </div>
              <p className="text-xs text-[#A0A0A0] mt-4">All times in IST (India Standard Time)</p>
            </Card>

            <Card variant="default" className="p-6 bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-lg border border-[rgba(74, 158, 255, 0.15)]">
              <h3 className="text-lg font-medium text-[#F0F0F0] mb-2">Need Immediate Help?</h3>
              <p className="text-sm text-[#A0A0A0] mb-4">
                Browse our FAQ section below for quick answers to common questions.
              </p>
              <button
                onClick={() => document.getElementById('faq-section')?.scrollIntoView({ behavior: 'smooth' })}
                className="w-full py-2.5 px-4 bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white rounded-xl text-sm font-medium transition-all"
              >
                Check FAQs
              </button>
            </Card>
          </div>
        </div>

        {/* FAQ Section */}
        <div id="faq-section" className="pt-4">
          <div className="flex items-center gap-3 mb-6">
            <HelpCircle className="size-5 text-[#4A9EFF]" />
            <h2 className="text-2xl font-semibold text-[#F0F0F0]">Frequently Asked Questions</h2>
          </div>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-[#2A2A2A] rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-[#1E1E1E] transition-colors"
                >
                  <span className="text-sm font-medium text-[#F0F0F0] pr-4">{faq.q}</span>
                  {openFaq === i
                    ? <ChevronUp className="size-4 text-[#4A9EFF] shrink-0" />
                    : <ChevronDown className="size-4 text-[#A0A0A0] shrink-0" />
                  }
                </button>
                {openFaq === i && (
                  <div className="px-5 pb-4 text-sm text-[#A0A0A0] leading-relaxed border-t border-[#2A2A2A] pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Footer Note */}
        <div className="pt-6 border-t border-[rgba(74, 158, 255, 0.15)]">
          <p className="text-center text-sm text-[#A0A0A0]">
            We typically respond to inquiries within 24 business hours.
            For urgent matters, please call us directly.
          </p>
        </div>
      </div>
    </div>
  );
}
