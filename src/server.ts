import * as dotenv from 'dotenv';
dotenv.config();
import http from 'http';
import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import { Server, Socket } from 'socket.io';
import { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } from "@aws-sdk/client-sqs";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

// AWS Konfiguration
const REGION = process.env.AWS_REGION ?? process.env.AWS_DEFAULT_REGION ?? "us-east-1";
const QUEUE_URL = process.env.SQS_QUEUE_URL ?? "https://sqs.us-east-1.amazonaws.com/219602461114/audio-upload-queue";
const S3_BUCKET_NAME = process.env.S3_BUCKET_NAME ?? "urban-pancake-audio-files";
const SQS_REGION = process.env.SQS_REGION ?? QUEUE_URL.match(/sqs\.([a-z0-9-]+)\.amazonaws\.com/)?.[1] ?? REGION;
const sqsClient = new SQSClient({ region: SQS_REGION });

// Ändere diese Zeile:
const s3Client = new S3Client({ 
  region: REGION,
  forcePathStyle: true // Oft notwendig, wenn der Bucket-Name Punkte enthält oder für bestimmte Regionen
});

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

// NEU: Stream-Proxy Route (umgeht S3-Direktzugriff und CORS)
app.get('/stream/:key', async (req, res) => {
  const key = decodeURIComponent(req.params.key);
  try {
    const command = new GetObjectCommand({ Bucket: S3_BUCKET_NAME, Key: key });
    const response = await s3Client.send(command);
    
    res.setHeader('Content-Type', 'audio/wav');
    (response.Body as any).pipe(res);
  } catch (err) {
    console.error("Streaming Fehler:", err);
    res.status(500).send("Fehler beim Laden der Audiodatei");
  }
});

// SQS Worker
async function startSQSWorker() {
  console.log("🚀 SQS Worker gestartet...");
  while (true) {
    try {
      const data = await sqsClient.send(new ReceiveMessageCommand({
        QueueUrl: QUEUE_URL,
        WaitTimeSeconds: 20,
        MaxNumberOfMessages: 1
      }));

      if (data.Messages) {
        for (const msg of data.Messages) {
          const body = JSON.parse(msg.Body!);
          const fileKey = decodeURIComponent(body.Records[0].s3.object.key.replace(/\+/g, " "));
          
          // Wir senden nur noch den Key, nicht mehr die Signed URL
          io.emit('new-file', { name: fileKey });

          await sqsClient.send(new DeleteMessageCommand({
            QueueUrl: QUEUE_URL,
            ReceiptHandle: msg.ReceiptHandle
          }));
        }
      }
    } catch (err) {
      console.error("SQS Fehler:", err);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

httpServer.listen(PORT, () => {
  console.log(`Server läuft auf http://localhost:${PORT}`);
  startSQSWorker();
});