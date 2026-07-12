import React, { useState } from "react";

interface URLFormProps {
  onURLShortened: () => void;
}

export const URLForm: React.FC<URLFormProps> = ({ onURLShortened }) => {
  const [originalUrl, setOriginalUrl] = useState("");
  const [shortenedUrl, setShortenedUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setShortenedUrl("");
    setLoading(true);

    try {
      const response = await fetch("/api/v1/shorten", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ original_url: originalUrl }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to shorten URL");
      }

      const data = await response.json();
      setShortenedUrl(`http://localhost/${data.short_code}`);
      setOriginalUrl("");
      onURLShortened();
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (shortenedUrl) {
      navigator.clipboard.writeText(shortenedUrl);
    }
  };

  return (
    <div style={{ marginBottom: "2rem", padding: "1rem", border: "1px solid #ccc", borderRadius: "4px" }}>
      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
          <input
            type="url"
            value={originalUrl}
            onChange={(e) => setOriginalUrl(e.target.value)}
            placeholder="Enter long URL (e.g. https://example.com)"
            required
            style={{ flex: 1, padding: "0.5rem" }}
          />
          <button type="submit" disabled={loading} style={{ padding: "0.5rem 1rem" }}>
            {loading ? "Shortening..." : "Shorten"}
          </button>
        </div>
      </form>

      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      {shortenedUrl && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem", backgroundColor: "#f0f0f0", borderRadius: "4px" }}>
          <span style={{ wordBreak: "break-all" }}>{shortenedUrl}</span>
          <button onClick={copyToClipboard} style={{ padding: "0.25rem 0.5rem" }}>
            Copy
          </button>
        </div>
      )}
    </div>
  );
};
