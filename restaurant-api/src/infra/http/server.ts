import 'dotenv/config';
import { app } from './app';
import { PORT } from 'config';

app.listen(PORT, () => {
  console.log(`[INFO] Server listening on http://localhost:${PORT}`);
});
