const router = require('express').Router();
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const { store } = require('../store');
const { signAccessToken, signRefreshToken, verifyToken, ACCESS_TOKEN_EXPIRES_IN } = require('../auth');
const { authenticate } = require('../middleware/authenticate');

// POST /auth/register
router.post('/auth/register', async (req, res, next) => {
  try {
    const { email, password, firstName, lastName, role } = req.body;

    const existing = [...store.users.values()].find(u => u.email === email);
    if (existing) {
      return res.status(409).json({
        code: 'DUPLICATE_EMAIL',
        message: 'A user with this email address already exists.',
      });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const userId = uuidv4();
    const now = new Date().toISOString();

    const user = { id: userId, email, password: hashedPassword, firstName, lastName, role, createdAt: now };
    store.users.set(userId, user);

    if (role === 'contributor') {
      // contributor profile could be extended here in a real domain
    }

    const payload = { sub: userId, email, role };
    const accessToken = signAccessToken(payload);
    const refreshToken = signRefreshToken(payload);

    res.status(201).json({
      accessToken,
      refreshToken,
      expiresIn: ACCESS_TOKEN_EXPIRES_IN,
      user: { id: userId, email, firstName, lastName, role },
    });
  } catch (err) {
    next(err);
  }
});

// POST /auth/login
router.post('/auth/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const user = [...store.users.values()].find(u => u.email === email);
    if (!user) {
      return res.status(401).json({
        code: 'INVALID_CREDENTIALS',
        message: 'The email or password provided is incorrect.',
      });
    }
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      return res.status(401).json({
        code: 'INVALID_CREDENTIALS',
        message: 'The email or password provided is incorrect.',
      });
    }
    const payload = { sub: user.id, email: user.email, role: user.role };
    const accessToken = signAccessToken(payload);
    const refreshToken = signRefreshToken(payload);
    res.status(200).json({
      accessToken,
      refreshToken,
      expiresIn: ACCESS_TOKEN_EXPIRES_IN,
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
      },
    });
  } catch (err) {
    next(err);
  }
});

// POST /auth/logout
router.post('/auth/logout', authenticate, (req, res) => {
  res.status(204).send();
});

// POST /auth/refresh
router.post('/auth/refresh', (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    let decoded;
    try {
      decoded = verifyToken(refreshToken);
    } catch (err) {
      return res.status(401).json({
        code: 'AUTHENTICATION_REQUIRED',
        message: 'Invalid or expired refresh token.',
      });
    }
    const user = store.users.get(decoded.sub);
    if (!user) {
      return res.status(401).json({
        code: 'AUTHENTICATION_REQUIRED',
        message: 'User not found.',
      });
    }
    const payload = { sub: user.id, email: user.email, role: user.role };
    const newAccessToken = signAccessToken(payload);
    const newRefreshToken = signRefreshToken(payload);
    res.status(200).json({
      accessToken: newAccessToken,
      refreshToken: newRefreshToken,
      expiresIn: ACCESS_TOKEN_EXPIRES_IN,
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
      },
    });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
