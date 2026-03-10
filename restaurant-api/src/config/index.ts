import path from 'path';
import fs from 'fs';
import dotenv from 'dotenv';

// Load .env from project root (works from both src/ and dist/)
const envPath = [path.resolve(__dirname, '../../.env'), path.resolve(__dirname, '../../../.env')].find((p) => fs.existsSync(p));
if (envPath) {
  dotenv.config({ path: envPath });
} else {
  dotenv.config(); // fallback: load from process.cwd()
}

export const SECRET = process.env.ACCESS_TOKEN_SECRET as string;
export const PORT = process.env.PORT || 3000;
