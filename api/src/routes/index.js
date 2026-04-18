const router = require('express').Router();

router.use(require('./auth'));
router.use('/items', require('./items'));

module.exports = router;
