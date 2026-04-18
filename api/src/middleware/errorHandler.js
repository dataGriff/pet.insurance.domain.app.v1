function errorHandler(err, req, res, next) {
  // express-openapi-validator errors
  if (err.status && err.errors) {
    return res.status(err.status).json({
      code: 'VALIDATION_ERROR',
      message: err.message || 'Validation error',
      details: err.errors.map(e => ({
        field: e.path || e.instancePath || 'unknown',
        issue: e.message || 'Invalid value',
      })),
    });
  }
  if (err.status) {
    return res.status(err.status).json({
      code: err.code || 'ERROR',
      message: err.message,
    });
  }
  console.error(err);
  res.status(500).json({
    code: 'INTERNAL_ERROR',
    message: 'An internal server error occurred.',
  });
}

module.exports = errorHandler;
