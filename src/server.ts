import 'dotenv/config';
import http from 'http';
import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import { Server, Socket } from 'socket.io';

interface MessagePayload {
  message: string;
  sentAt: number;
}

const app: Application = express();
const httpServer = http.createServer(app);
const io = new Server(httpServer, { cors: { origin: '*' } });
const PORT: number = parseInt(process.env.PORT ?? '3000', 10);

app.use(cors());
app.use(express.json());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get('/', (_req: Request, res: Response) => {
  res.render('index');
});

io.on('connection', (socket: Socket) => {
  console.log(`🔌 Client verbunden: ${socket.id}`);

  socket.on('message', ({ message, sentAt }: MessagePayload) => {
    const receivedAt = Date.now();
    const duration = receivedAt - sentAt;

    console.log('─────────────────────────────────');
    console.log(`📨 Nachricht : "${message}"`);
    console.log(`⏱  Dauer     : ${duration} ms`);
    console.log(`🕒 Empfangen : ${new Date(receivedAt).toISOString()}`);
    console.log('─────────────────────────────────');

    socket.emit('message:ack', { ok: true, duration });
  });

  socket.on('disconnect', () => {
    console.log(`❌ Client getrennt: ${socket.id}`);
  });
});

httpServer.listen(PORT, () => {
  console.log(`Server läuft auf http://localhost:${PORT}`);
});
