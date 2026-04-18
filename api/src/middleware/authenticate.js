const { verifyToken } = require('../auth');

function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      code: 'AUTHENTICATION_REQUIRED',
      message: 'A valid bearer token is required to access this resource.',
    });
  }
  const token = authHeader.slice(7);
  try {
    const decoded = verifyToken(token);
    req.user = decoded;
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({
        code: 'TOKEN_EXPIRED',
        message: 'The access token has expired. Please refresh your session.',
      });
    }
    return res.status(401).json({
      code: 'AUTHENTICATION_REQUIRED',
      message: 'A valid bearer token is required to access this resource.',
    });
  }
}

function requireRole(role) {
  return (req, res, next) => {
    if (req.user.role !== role) {
      return res.status(403).json({
        code: 'FORBIDDEN',
        message: 'Your role does not have permission to perform this action.',
      });
    }
    next();
  };
}

module.exports = { authenticate, requireRole };
