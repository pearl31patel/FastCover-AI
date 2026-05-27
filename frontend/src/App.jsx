import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FileText, Download, Sparkles, UploadCloud } from "lucide-react";
import logo from "./assets/transparent-logo.png";

const API_URL = "https://fastcover-ai.onrender.com";

export default function App() {
  const [form, setForm] = useState({
    name: "",
    company: "",
    role: "",
    job_description: "",
  });

  const [resume, setResume] = useState(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [showContact, setShowContact] = useState(false);
  const [contactLoading, setContactLoading] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: "",
    email: "",
    phone: "",
    details: "",
  });

  const updateForm = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const buildData = () => {
    const data = new FormData();
    data.append("resume", resume);
    data.append("name", form.name);
    data.append("company", form.company);
    data.append("role", form.role);
    data.append("job_description", form.job_description);
    return data;
  };

  const previewLetter = async () => {
    if (!resume) return alert("Please upload your resume PDF.");
    setLoading(true);

    try {
      const res = await axios.post(
        `${API_URL}/preview-cover-letter`,
        buildData()
      );
      setPreview(res.data.cover_letter);
    } catch {
      alert("Something went wrong.");
    }

    setLoading(false);
  };

  const downloadPdf = async () => {
    if (!resume) return alert("Please upload your resume PDF.");
    setLoading(true);

    try {
      const res = await axios.post(
        `${API_URL}/generate-cover-letter`,
        buildData(),
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      const fileName = `${form.company
        .trim()
        .toUpperCase()
        .replaceAll(" ", "_")}_COVER_LETTER.pdf`;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      alert("PDF download failed.");
    }

    setLoading(false);
  };

  const isFormValid =
    form.name.trim() &&
    form.company.trim() &&
    form.role.trim() &&
    form.job_description.trim() &&
    resume;

  const LoadingBar = () => (
    <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden mt-4">
      <motion.div
        className="h-full bg-indigo-600"
        initial={{ x: "-100%" }}
        animate={{ x: "100%" }}
        transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
      />
    </div>
  );

  const updateContactForm = (e) => {
    setContactForm({ ...contactForm, [e.target.name]: e.target.value });
  };

  const submitContactForm = async (e) => {
    e.preventDefault();

    if (
      !contactForm.name.trim() ||
      !contactForm.email.trim() ||
      !contactForm.phone.trim() ||
      !contactForm.details.trim()
    ) {
      alert("Please fill all fields.");
      return;
    }

    setContactLoading(true);

    try {
      const data = new FormData();
      data.append("name", contactForm.name);
      data.append("email", contactForm.email);
      data.append("phone", contactForm.phone);
      data.append("details", contactForm.details);

      await axios.post(`${API_URL}/contact`, data);

      alert("Message sent successfully.");
      setContactForm({ name: "", email: "", phone: "", details: "" });
      setShowContact(false);
    } catch {
      alert("Failed to send message.");
    }

    setContactLoading(false);
  };

  return (
    <div className="min-h-screen text-slate-900">
      <header className="bg-white/80 backdrop-blur border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2 font-bold text-xl">
            {/* <img src={logo} alt="FastCover AI logo" className="h-12 w-auto" /> */}
            {/* <img src={logo} alt="FastCover AI logo" className="h-10 md:h-24 w-auto object-contain" /> */}
            <img
              src={logo}
              alt="FastCover AI logo"
              className="object-contain"
              style={{
                height: "80px",
                objectPosition: "center",
              }}
            />
          </div>
          <nav className="hidden md:flex gap-6 text-sm text-slate-600">
            <a href="#generator">Generator</a>
            <a href="#features">Features</a>
            <a href="#future">Premium Future</a>
            <button
              onClick={() => setShowContact(true)}
              className="text-slate-600 hover:text-indigo-600"
            >
              Contact Us
            </button>
          </nav>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-6 py-16 grid lg:grid-cols-2 gap-10 items-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-indigo-600 font-semibold mb-3">
            Free AI based Cover Letter Generator
          </p>
          <h1 className="text-4xl md:text-6xl font-bold leading-tight">
            Create a personalized cover letter in seconds.
          </h1>
          <p className="mt-6 text-lg text-slate-600">
            Upload your resume, paste the job description, enter company
            details, and download a clean PDF cover letter.
          </p>
          <div className="mt-8 flex gap-4">
            <a
              href="#generator"
              className="bg-indigo-600 text-white px-6 py-3 rounded-xl shadow hover:bg-indigo-700"
            >
              Start Free
            </a>
            <a
              href="#features"
              className="bg-white px-6 py-3 rounded-xl shadow border"
            >
              View Features
            </a>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-3xl shadow-xl p-8 border"
        >
          <FileText size={48} className="text-indigo-600 mb-4" />
          <h2 className="text-2xl font-bold mb-3">Built for job seekers</h2>
          <p className="text-slate-600">
            FastCover AI helps users create simple, professional, and
            ATS-friendly cover letters without manual formatting.
          </p>
        </motion.div>
      </section>

      <section id="generator" className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, x: -25 }}
            whileInView={{ opacity: 1, x: 0 }}
            className="bg-white rounded-3xl shadow-xl p-6 border"
          >
            <h2 className="text-2xl font-bold mb-6">Generate Cover Letter</h2>

            <div className="space-y-4">
              <input
                name="name"
                placeholder="Your full name"
                onChange={updateForm}
                className="w-full border rounded-xl px-4 py-3"
              />

              <input
                name="company"
                placeholder="Company name"
                onChange={updateForm}
                className="w-full border rounded-xl px-4 py-3"
              />

              <input
                name="role"
                placeholder="Role title"
                onChange={updateForm}
                className="w-full border rounded-xl px-4 py-3"
              />

              <label className="border border-dashed rounded-xl p-5 flex items-center justify-between gap-3 cursor-pointer">
                <div className="flex items-center gap-3">
                  <UploadCloud className="text-indigo-600" />
                  <span>{resume ? resume.name : "Upload Resume PDF"}</span>
                </div>

                {resume && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      setResume(null);
                    }}
                    className="text-sm bg-red-100 text-red-600 px-3 py-1 rounded-lg hover:bg-red-200"
                  >
                    Remove
                  </button>
                )}

                <input
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setResume(e.target.files[0])}
                  className="hidden"
                />
              </label>

              <textarea
                name="job_description"
                placeholder="Paste job requirements / job description here"
                rows="8"
                onChange={updateForm}
                className="w-full border rounded-xl px-4 py-3"
              />

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={previewLetter}
                  disabled={loading || !isFormValid}
                  className={`flex-1 py-3 rounded-xl ${
                    loading || !isFormValid
                      ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                      : "bg-slate-900 text-white hover:bg-slate-800"
                  }`}
                >
                  {loading ? "Generating..." : "Preview Letter"}
                </button>

                <button
                  onClick={downloadPdf}
                  disabled={loading || !isFormValid}
                  className={`flex-1 py-3 rounded-xl flex justify-center items-center gap-2 ${
                    loading || !isFormValid
                      ? "bg-indigo-300 text-white cursor-not-allowed"
                      : "bg-indigo-600 text-white hover:bg-indigo-700"
                  }`}
                >
                  <Download size={18} />
                  {loading ? "Preparing PDF..." : "Download PDF"}
                </button>
              </div>
              {loading && (
                <div className="mt-4">
                  <LoadingBar />
                  <p className="text-sm text-slate-500 mt-2 text-center">
                    Generating your cover letter, please wait...
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 25 }}
            whileInView={{ opacity: 1, x: 0 }}
            className="bg-white rounded-3xl shadow-xl p-6 border min-h-[500px]"
          >
            <h2 className="text-2xl font-bold mb-6">Preview</h2>
            <pre className="whitespace-pre-wrap text-sm text-slate-700 leading-7">
              {preview || "Your generated cover letter will appear here."}
            </pre>
          </motion.div>
        </div>
      </section>

      <section id="features" className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-10">
          Why users will like it
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            "Free to use",
            "Resume-aware writing",
            "Downloadable PDF",
            "Clean responsive UI",
            "Job description matching",
            "Fast cover letter preview",
          ].map((item) => (
            <motion.div
              key={item}
              whileHover={{ y: -6 }}
              className="bg-white rounded-2xl p-6 shadow border"
            >
              <h3 className="font-bold text-lg">{item}</h3>
              <p className="text-slate-600 mt-2">
                Simple, fast, and helpful for job seekers.
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="future" className="bg-slate-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold">
            More helpful features are coming soon
          </h2>
          <p className="mt-4 text-slate-300">
            Soon you will be able to use better cover letter templates, choose
            tone options, create a user login, save generated letters, check
            resume keyword match scores, find missing ATS keywords, use Chrome
            extension auto-fill, and unlock premium AI rewrite mode in one
            place.
          </p>
        </div>
      </section>

      {showContact && (
        <div className="fixed inset-0 bg-black/50 z-[999] flex items-center justify-center px-4">
          <div className="bg-white rounded-3xl shadow-2xl p-6 w-full max-w-lg relative">
            <button
              onClick={() => setShowContact(false)}
              className="absolute top-4 right-4 text-slate-500 hover:text-slate-900"
            >
              ✕
            </button>

            <h2 className="text-2xl font-bold mb-2">Contact Us</h2>
            <p className="text-slate-500 mb-6">
              Share your concern or feedback. We will review it soon.
            </p>

            <form onSubmit={submitContactForm} className="space-y-4">
              <input
                name="name"
                value={contactForm.name}
                onChange={updateContactForm}
                placeholder="Your name"
                required
                className="w-full border rounded-xl px-4 py-3"
              />

              <input
                name="email"
                type="email"
                value={contactForm.email}
                onChange={updateContactForm}
                placeholder="Your email"
                required
                className="w-full border rounded-xl px-4 py-3"
              />

              <input
                name="phone"
                value={contactForm.phone}
                onChange={updateContactForm}
                placeholder="Phone number"
                required
                className="w-full border rounded-xl px-4 py-3"
              />

              <textarea
                name="details"
                value={contactForm.details}
                onChange={updateContactForm}
                placeholder="Write your concern or message"
                required
                rows="5"
                className="w-full border rounded-xl px-4 py-3"
              />

              <button
                type="submit"
                disabled={contactLoading}
                className="w-full bg-indigo-600 text-white py-3 rounded-xl hover:bg-indigo-700 disabled:bg-indigo-300"
              >
                {contactLoading ? "Sending..." : "Submit"}
              </button>
            </form>
          </div>
        </div>
      )}

      <footer className="bg-white border-t py-6 text-center text-slate-500">
        © 2026 FastCover AI. Built to help job seekers apply faster.
      </footer>
    </div>
  );
}
