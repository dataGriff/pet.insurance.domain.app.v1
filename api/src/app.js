const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { OpenApiValidator } = require('express-openapi-validator');
const path = require('path');

const app = express();

const allowedOrigins = process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : [];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (e.g. curl, Postman, Bruno CLI)
    if (!origin) return callback(null, true);
    if (allowedOrigins.includes(origin)) return callback(null, true);
    callback(new Error(`CORS: origin '${origin}' not allowed`));
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
}));

app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 500,
  standardHeaders: true,
  legacyHeaders: false,
  message: { code: 'TOO_MANY_REQUESTS', message: 'Too many requests, please try again later.' },
}));

app.use(express.json());

app.use(
  require('express-openapi-validator').middleware({
    apiSpec: path.join(__dirname, '../../docs/specifications/contracts/openapi.yaml'),
    validateRequests: true,
    validateResponses: false,
    ignorePaths: /^(?!\/v1)/,
    fileUploader: { storage: require('multer').memoryStorage() },
  })
);

const routes = require('./routes/index');
app.use('/v1', routes);

const errorHandler = require('./middleware/errorHandler');
app.use(errorHandler);

module.exports = app;
