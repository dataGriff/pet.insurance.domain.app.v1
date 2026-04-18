const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcryptjs');
const { store, resetStore } = require('../src/store');
const { signAccessToken } = require('../src/auth');
const app = require('../src/app');

async function createUser(email, password, firstName, lastName, role) {
  const hashedPassword = await bcrypt.hash(password, 10);
  const userId = uuidv4();
  const now = new Date().toISOString();
  const user = { id: userId, email, password: hashedPassword, firstName, lastName, role, createdAt: now };
  store.users.set(userId, user);
  return user;
}

function tokenForUser(user) {
  return signAccessToken({ sub: user.id, email: user.email, role: user.role });
}

async function createContributorToken(overrides = {}) {
  const email = overrides.email || `contributor-${uuidv4()}@test.com`;
  const user = await createUser(email, 'password123', 'Test', 'Contributor', 'contributor');
  return { token: tokenForUser(user), user };
}

async function createViewerToken(overrides = {}) {
  const email = overrides.email || `viewer-${uuidv4()}@test.com`;
  const user = await createUser(email, 'password123', 'Test', 'Viewer', 'viewer');
  return { token: tokenForUser(user), user };
}

function seedItem(contributorId, overrides = {}) {
  const now = new Date().toISOString();
  const item = {
    id: uuidv4(),
    name: 'Sample Item',
    description: 'A sample item description.',
    status: 'active',
    contributorId,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
  store.items.set(item.id, item);
  return item;
}

module.exports = {
  app,
  store,
  resetStore,
  createUser,
  createContributorToken,
  createViewerToken,
  seedItem,
  tokenForUser,
};
