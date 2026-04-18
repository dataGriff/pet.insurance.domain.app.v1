const router = require('express').Router();
const { v4: uuidv4 } = require('uuid');
const { store } = require('../store');
const { authenticate, requireRole } = require('../middleware/authenticate');

// GET /items — list all items (any authenticated role)
router.get('/', authenticate, (req, res) => {
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);
  const pageSize = Math.min(100, Math.max(1, parseInt(req.query.pageSize, 10) || 20));
  const all = [...store.items.values()];
  const total = all.length;
  const data = all.slice((page - 1) * pageSize, page * pageSize);
  res.status(200).json({ data, pagination: { page, pageSize, total } });
});

// POST /items — add an item (contributor only)
router.post('/', authenticate, requireRole('contributor'), (req, res) => {
  const { name, description } = req.body;
  const now = new Date().toISOString();
  const item = {
    id: uuidv4(),
    name,
    description: description ?? null,
    status: 'active',
    contributorId: req.user.sub,
    createdAt: now,
    updatedAt: now,
  };
  store.items.set(item.id, item);
  res.status(201).json(item);
});

// GET /items/:itemId — get a single item (any authenticated role)
router.get('/:itemId', authenticate, (req, res) => {
  const item = store.items.get(req.params.itemId);
  if (!item) {
    return res.status(404).json({ code: 'RESOURCE_NOT_FOUND', message: 'Item not found.' });
  }
  res.status(200).json(item);
});

// PATCH /items/:itemId — edit an item (contributor, own only)
// Note: field validation (e.g. status enum) is enforced upstream by the OpenAPI validator middleware.
router.patch('/:itemId', authenticate, requireRole('contributor'), (req, res) => {
  const item = store.items.get(req.params.itemId);
  if (!item) {
    return res.status(404).json({ code: 'RESOURCE_NOT_FOUND', message: 'Item not found.' });
  }
  if (item.contributorId !== req.user.sub) {
    return res.status(403).json({ code: 'FORBIDDEN', message: 'You can only edit your own items.' });
  }
  const { name, description, status } = req.body;
  if (name !== undefined) item.name = name;
  if (description !== undefined) item.description = description;
  if (status !== undefined) item.status = status;
  item.updatedAt = new Date().toISOString();
  store.items.set(item.id, item);
  res.status(200).json(item);
});

// DELETE /items/:itemId — remove an item (contributor, own only)
router.delete('/:itemId', authenticate, requireRole('contributor'), (req, res) => {
  const item = store.items.get(req.params.itemId);
  if (!item) {
    return res.status(404).json({ code: 'RESOURCE_NOT_FOUND', message: 'Item not found.' });
  }
  if (item.contributorId !== req.user.sub) {
    return res.status(403).json({ code: 'FORBIDDEN', message: 'You can only remove your own items.' });
  }
  store.items.delete(item.id);
  res.status(204).send();
});

module.exports = router;
