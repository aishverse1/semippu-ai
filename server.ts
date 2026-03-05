import express from "express";
import { createServer as createViteServer } from "vite";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import cors from "cors";
import dotenv from "dotenv";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const db = new Database("database.db");

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS otps (
    phone_number TEXT PRIMARY KEY,
    otp TEXT NOT NULL,
    expires_at DATETIME NOT NULL
  );
`);

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  const JWT_SECRET = process.env.JWT_SECRET || "semippu_secret_key";

  app.post("/api/ai/predict", async (req, res) => {
    try {
      const body = JSON.stringify(req.body);
      console.log("[AI] Forwarding body:", body);
      const response = await fetch(`${FASTAPI_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
      });
      const data = await response.json();
      if (!response.ok) {
        return res.status(response.status).json({ error: data.detail || "AI server error" });
      }
      res.json(data);
    } catch (err: any) {
      console.error("[AI] Error:", err.message);
      res.status(503).json({ error: "AI server is not reachable." });
    }
  });

  app.get("/api/ai/plan/:userId", async (req, res) => {
    try {
      const { userId } = req.params;
      const response = await fetch(`${FASTAPI_URL}/get-plan/${encodeURIComponent(userId)}`);
      const data = await response.json();
      if (!response.ok) {
        return res.status(response.status).json({ error: data.detail || "AI server error" });
      }
      res.json(data);
    } catch (err: any) {
      res.status(503).json({ error: "AI server is not reachable." });
    }
  });

  app.post("/api/auth/register-otp", (req, res) => {
    const { phoneNumber } = req.body;
    if (!phoneNumber || !/^\+?[1-9]\d{1,14}$/.test(phoneNumber)) {
      return res.status(400).json({ error: "Invalid phone number format" });
    }
    const existingUser = db.prepare("SELECT * FROM users WHERE phone_number = ?").get(phoneNumber);
    if (existingUser) {
      return res.status(400).json({ error: "User already exists" });
    }
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = new Date(Date.now() + 5 * 60000).toISOString();
    db.prepare(`
      INSERT INTO otps (phone_number, otp, expires_at) 
      VALUES (?, ?, ?) 
      ON CONFLICT(phone_number) DO UPDATE SET otp=excluded.otp, expires_at=excluded.expires_at
    `).run(phoneNumber, otp, expiresAt);
    console.log(`[DEBUG] OTP for ${phoneNumber}: ${otp}`);
    res.json({ message: "OTP sent successfully" });
  });

  app.post("/api/auth/register-verify", async (req, res) => {
    const { phoneNumber, otp, password, isAdmin } = req.body;
    if (!phoneNumber || !otp || !password) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const otpRecord = db.prepare("SELECT * FROM otps WHERE phone_number = ?").get(phoneNumber) as any;
    if (!otpRecord || otpRecord.otp !== otp || new Date(otpRecord.expires_at) < new Date()) {
      return res.status(400).json({ error: "Invalid or expired OTP" });
    }
    try {
      const hashedPassword = await bcrypt.hash(password, 10);
      db.prepare("INSERT INTO users (phone_number, password, is_admin) VALUES (?, ?, ?)")
        .run(phoneNumber, hashedPassword, isAdmin ? 1 : 0);
      db.prepare("DELETE FROM otps WHERE phone_number = ?").run(phoneNumber);
      const token = jwt.sign({ phoneNumber, isAdmin }, JWT_SECRET, { expiresIn: "7d" });
      res.json({ message: "Registration successful", token, user: { phoneNumber, isAdmin: !!isAdmin } });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  app.post("/api/auth/login", async (req, res) => {
    const { phoneNumber, password } = req.body;
    if (!phoneNumber || !password) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const user = db.prepare("SELECT * FROM users WHERE phone_number = ?").get(phoneNumber) as any;
    if (!user) return res.status(401).json({ error: "Invalid phone number or password" });
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) return res.status(401).json({ error: "Invalid phone number or password" });
    const token = jwt.sign(
      { phoneNumber: user.phone_number, isAdmin: !!user.is_admin },
      JWT_SECRET,
      { expiresIn: "7d" }
    );
    res.json({ message: "Login successful", token, user: { phoneNumber: user.phone_number, isAdmin: !!user.is_admin } });
  });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, "dist")));
    app.get("*", (req, res) => {
      res.sendFile(path.join(__dirname, "dist", "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`✅ Express server running on http://localhost:${PORT}`);
    console.log(`🤖 AI requests forwarded to ${FASTAPI_URL}`);
  });
}

startServer();
