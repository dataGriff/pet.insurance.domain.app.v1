const request = require('supertest');
const { app, resetStore, createContributorToken, createViewerToken, seedItem } = require('./helpers');

beforeEach(() => resetStore());

describe('Items routes', () => {
  describe('GET /v1/items', () => {
    it('returns empty list when no items exist', async () => {
      const { token } = await createContributorToken();
      const res = await request(app).get('/v1/items').set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
      expect(res.body.data).toEqual([]);
      expect(res.body.pagination.total).toBe(0);
    });

    it('returns list of items', async () => {
      const { token, user } = await createContributorToken();
      seedItem(user.id);
      seedItem(user.id);
      const res = await request(app).get('/v1/items').set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
      expect(res.body.data).toHaveLength(2);
      expect(res.body.pagination.total).toBe(2);
    });

    it('viewers can list items', async () => {
      const { token: cToken, user } = await createContributorToken();
      seedItem(user.id);
      const { token: vToken } = await createViewerToken();
      const res = await request(app).get('/v1/items').set('Authorization', `Bearer ${vToken}`);
      expect(res.status).toBe(200);
      expect(res.body.data).toHaveLength(1);
    });

    it('returns 401 without token', async () => {
      const res = await request(app).get('/v1/items');
      expect(res.status).toBe(401);
    });
  });

  describe('POST /v1/items', () => {
    it('adds an item as contributor', async () => {
      const { token } = await createContributorToken();
      const res = await request(app).post('/v1/items')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'My Item', description: 'A great item' });
      expect(res.status).toBe(201);
      expect(res.body.id).toBeDefined();
      expect(res.body.name).toBe('My Item');
      expect(res.body.description).toBe('A great item');
      expect(res.body.status).toBe('active');
      expect(res.body.contributorId).toBeDefined();
      expect(res.body.createdAt).toBeDefined();
      expect(res.body.updatedAt).toBeDefined();
    });

    it('adds an item with null description when omitted', async () => {
      const { token } = await createContributorToken();
      const res = await request(app).post('/v1/items')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'No Description Item' });
      expect(res.status).toBe(201);
      expect(res.body.description).toBeNull();
    });

    it('returns 403 when viewer tries to add', async () => {
      const { token } = await createViewerToken();
      const res = await request(app).post('/v1/items')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Viewer Item' });
      expect(res.status).toBe(403);
    });

    it('returns 401 without token', async () => {
      const res = await request(app).post('/v1/items').send({ name: 'Item' });
      expect(res.status).toBe(401);
    });
  });

  describe('GET /v1/items/:itemId', () => {
    it('returns an item by id', async () => {
      const { token, user } = await createContributorToken();
      const item = seedItem(user.id);
      const res = await request(app).get(`/v1/items/${item.id}`).set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
      expect(res.body.id).toBe(item.id);
      expect(res.body.name).toBe(item.name);
    });

    it('viewers can get an item', async () => {
      const { user } = await createContributorToken();
      const item = seedItem(user.id);
      const { token: vToken } = await createViewerToken();
      const res = await request(app).get(`/v1/items/${item.id}`).set('Authorization', `Bearer ${vToken}`);
      expect(res.status).toBe(200);
      expect(res.body.id).toBe(item.id);
    });

    it('returns 404 for non-existent item', async () => {
      const { token } = await createContributorToken();
      const res = await request(app)
        .get('/v1/items/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(404);
      expect(res.body.code).toBe('RESOURCE_NOT_FOUND');
    });

    it('returns 401 without token', async () => {
      const res = await request(app).get('/v1/items/00000000-0000-0000-0000-000000000000');
      expect(res.status).toBe(401);
    });
  });

  describe('PATCH /v1/items/:itemId', () => {
    it('contributor can edit their own item', async () => {
      const { token, user } = await createContributorToken();
      const item = seedItem(user.id);
      const res = await request(app).patch(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Updated Name', status: 'archived' });
      expect(res.status).toBe(200);
      expect(res.body.name).toBe('Updated Name');
      expect(res.body.status).toBe('archived');
    });

    it('returns 403 when editing another contributor\'s item', async () => {
      const { user: creator } = await createContributorToken();
      const item = seedItem(creator.id);
      const { token: otherToken } = await createContributorToken();
      const res = await request(app).patch(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${otherToken}`)
        .send({ name: 'Stolen Update' });
      expect(res.status).toBe(403);
    });

    it('returns 403 when viewer tries to edit', async () => {
      const { user } = await createContributorToken();
      const item = seedItem(user.id);
      const { token: vToken } = await createViewerToken();
      const res = await request(app).patch(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${vToken}`)
        .send({ name: 'Viewer Update' });
      expect(res.status).toBe(403);
    });

    it('returns 404 for non-existent item', async () => {
      const { token } = await createContributorToken();
      const res = await request(app)
        .patch('/v1/items/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'X' });
      expect(res.status).toBe(404);
    });
  });

  describe('DELETE /v1/items/:itemId', () => {
    it('contributor can remove their own item', async () => {
      const { token, user } = await createContributorToken();
      const item = seedItem(user.id);
      const res = await request(app).delete(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(204);
    });

    it('returns 403 when removing another contributor\'s item', async () => {
      const { user: creator } = await createContributorToken();
      const item = seedItem(creator.id);
      const { token: otherToken } = await createContributorToken();
      const res = await request(app).delete(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${otherToken}`);
      expect(res.status).toBe(403);
    });

    it('returns 403 when viewer tries to remove', async () => {
      const { user } = await createContributorToken();
      const item = seedItem(user.id);
      const { token: vToken } = await createViewerToken();
      const res = await request(app).delete(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${vToken}`);
      expect(res.status).toBe(403);
    });

    it('returns 404 for non-existent item', async () => {
      const { token } = await createContributorToken();
      const res = await request(app)
        .delete('/v1/items/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(404);
    });
  });
});
